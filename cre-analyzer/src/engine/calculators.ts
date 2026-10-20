/**
 * CRE / financial calculator primitives. Pure functions, no I/O.
 *
 * These are the standard back-of-envelope real-estate calculations that sit
 * underneath the full Lease vs. Buy model. They reuse the money-safe finance
 * helpers (decimal.js) so results agree with the analysis engine.
 */
import Decimal from 'decimal.js';
import {
  amortizationSchedule,
  annualMortgagePayment,
  irr as irrCalc,
  money,
  npv as npvCalc,
  round,
} from './finance';

// ---------------------------------------------------------------------------
// Cap rate <-> value <-> NOI (the appraisal triangle)
// ---------------------------------------------------------------------------

/** Cap rate = NOI / Value. */
export function capRate(noi: number, value: number): number {
  if (value <= 0) throw new Error('Value must be greater than 0.');
  return round(new Decimal(noi).div(value), 6);
}

/** Value = NOI / Cap rate. */
export function valueFromCap(noi: number, rate: number): number {
  if (rate <= 0) throw new Error('Cap rate must be greater than 0.');
  return money(new Decimal(noi).div(rate));
}

/** NOI = Value * Cap rate. */
export function noiFromCap(value: number, rate: number): number {
  return money(new Decimal(value).mul(rate));
}

// ---------------------------------------------------------------------------
// Income
// ---------------------------------------------------------------------------

export interface NoiInputs {
  grossPotentialIncome: number;
  vacancyRate?: number; // decimal, e.g. 0.05
  otherIncome?: number;
  operatingExpenses: number;
}

export interface NoiResult {
  grossPotentialIncome: number;
  vacancyLoss: number;
  effectiveGrossIncome: number;
  operatingExpenses: number;
  noi: number;
}

/** Net Operating Income = EGI - OpEx, with vacancy and other income. */
export function computeNoi(inputs: NoiInputs): NoiResult {
  const gpi = new Decimal(inputs.grossPotentialIncome);
  const vacancyLoss = gpi.mul(inputs.vacancyRate ?? 0);
  const egi = gpi.minus(vacancyLoss).plus(inputs.otherIncome ?? 0);
  const noi = egi.minus(inputs.operatingExpenses);
  return {
    grossPotentialIncome: money(gpi),
    vacancyLoss: money(vacancyLoss),
    effectiveGrossIncome: money(egi),
    operatingExpenses: money(inputs.operatingExpenses),
    noi: money(noi),
  };
}

// ---------------------------------------------------------------------------
// Returns & coverage
// ---------------------------------------------------------------------------

/** Cash-on-cash = annual pre-tax cash flow / equity invested. */
export function cashOnCash(annualCashFlow: number, equityInvested: number): number {
  if (equityInvested <= 0) throw new Error('Equity invested must be greater than 0.');
  return round(new Decimal(annualCashFlow).div(equityInvested), 6);
}

/** Debt-service coverage ratio = NOI / annual debt service. */
export function dscr(noi: number, annualDebtService: number): number {
  if (annualDebtService <= 0) throw new Error('Debt service must be greater than 0.');
  return round(new Decimal(noi).div(annualDebtService), 4);
}

/** Gross rent multiplier = price / gross (annual) income. */
export function grossRentMultiplier(price: number, grossAnnualIncome: number): number {
  if (grossAnnualIncome <= 0) throw new Error('Gross income must be greater than 0.');
  return round(new Decimal(price).div(grossAnnualIncome), 4);
}

/** Break-even occupancy = (OpEx + debt service) / gross potential income. */
export function breakEvenOccupancy(
  operatingExpenses: number,
  annualDebtService: number,
  grossPotentialIncome: number
): number {
  if (grossPotentialIncome <= 0)
    throw new Error('Gross potential income must be greater than 0.');
  return round(
    new Decimal(operatingExpenses).plus(annualDebtService).div(grossPotentialIncome),
    6
  );
}

// ---------------------------------------------------------------------------
// Mortgage
// ---------------------------------------------------------------------------

export interface MortgageInputs {
  principal: number;
  annualRate: number;
  amortYears: number;
  /** Years to show/summarize; defaults to full amortization. */
  termYears?: number;
}

export interface MortgageResult {
  principal: number;
  annualRate: number;
  amortYears: number;
  annualPayment: number;
  monthlyPayment: number;
  termYears: number;
  totalPaidOverTerm: number;
  totalInterestOverTerm: number;
  balanceAtTermEnd: number;
  schedule: { year: number; interest: number; principal: number; balanceEnd: number }[];
}

/** Full mortgage summary + annual amortization schedule. */
export function mortgage(inputs: MortgageInputs): MortgageResult {
  const term = inputs.termYears ?? inputs.amortYears;
  const annualPayment = annualMortgagePayment(
    inputs.principal,
    inputs.annualRate,
    inputs.amortYears
  );
  const schedule = amortizationSchedule(
    inputs.principal,
    inputs.annualRate,
    inputs.amortYears,
    term
  );
  const totalInterest = schedule.reduce((acc, r) => acc + r.interest, 0);
  const totalPrincipal = schedule.reduce((acc, r) => acc + r.principal, 0);
  return {
    principal: money(inputs.principal),
    annualRate: inputs.annualRate,
    amortYears: inputs.amortYears,
    annualPayment,
    monthlyPayment: money(annualPayment / 12),
    termYears: term,
    totalPaidOverTerm: money(totalPrincipal + totalInterest),
    totalInterestOverTerm: money(totalInterest),
    balanceAtTermEnd: schedule.length ? schedule[schedule.length - 1].balanceEnd : money(inputs.principal),
    schedule,
  };
}

/**
 * Maximum supportable loan given NOI, a required DSCR, and loan terms.
 * Backs out the payment the property can cover, then the principal that payment
 * amortizes (present value of an annuity).
 */
export function maxLoanFromDscr(
  noi: number,
  requiredDscr: number,
  annualRate: number,
  amortYears: number
): number {
  if (requiredDscr <= 0) throw new Error('DSCR must be greater than 0.');
  const supportablePayment = new Decimal(noi).div(requiredDscr);
  const r = new Decimal(annualRate);
  if (r.lte(0)) return money(supportablePayment.mul(amortYears));
  // PV = PMT * (1 - (1+r)^-n) / r
  const factor = new Decimal(1).minus(r.plus(1).pow(-amortYears)).div(r);
  return money(supportablePayment.mul(factor));
}

// ---------------------------------------------------------------------------
// Time value of money (thin wrappers over finance.ts for the CLI)
// ---------------------------------------------------------------------------

/** NPV of a cash-flow vector (index 0 = time 0). */
export function npv(rate: number, cashFlows: number[]): number {
  return npvCalc(rate, cashFlows);
}

/** IRR of a cash-flow vector (index 0 = time 0). */
export function irr(cashFlows: number[]): number {
  return irrCalc(cashFlows);
}
