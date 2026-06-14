/**
 * BUY scenario (owner-occupied). Pure functions.
 *
 * Models the full ownership life-cycle: acquisition + financing, ten years of
 * tax-inclusive NOI and debt service with a depreciation/interest tax shield,
 * then a terminal sale at an exit cap with selling costs, loan payoff, capital
 * gains and depreciation recapture.
 *
 * Every NOI here is tax-inclusive: property tax is projected from the subject's
 * POST-reassessment bill (not its stale current bill) and grown subject to any
 * statutory cap.
 */
import Decimal from 'decimal.js';
import {
  AnalysisAssumptions,
  BuyAnalysis,
  MarketDerivation,
  SubjectProperty,
  YearlyBuyCashFlow,
} from '../types';
import {
  amortizationSchedule,
  annualMortgagePayment,
  grow,
  irr,
  money,
  npv,
} from './finance';
import { applyAssessmentCap } from './taxNormalizer';

/** Project the subject's property tax in a given hold year (post-reassessment). */
export function projectedPropertyTax(
  subject: SubjectProperty,
  assumptions: AnalysisAssumptions,
  year: number
): number {
  const base = subject.taxContext.estimatedPostTransactionTax;
  // Year 1 is the reset basis; subsequent years grow subject to the cap.
  return money(
    applyAssessmentCap(
      base,
      subject.taxContext.annualAssessmentCap,
      year - 1,
      assumptions.taxGrowthRate
    )
  );
}

/** Net operating income (tax-inclusive) for a given hold year. */
export function noiForYear(
  subject: SubjectProperty,
  market: MarketDerivation,
  assumptions: AnalysisAssumptions,
  year: number
): { noi: number; grossRent: number; propertyTax: number; nonTaxOpEx: number } {
  const sqft = subject.buildingSqFt;
  const rentPerSqFt = grow(
    market.avgSubjectAdjustedRent,
    assumptions.rentGrowthRate,
    year - 1
  );
  const grossRent = new Decimal(rentPerSqFt).mul(sqft).toNumber();

  const propertyTax = projectedPropertyTax(subject, assumptions, year);
  const nonTaxOpEx = new Decimal(
    grow(market.avgNonTaxOpExPerSqFt, assumptions.rentGrowthRate, year - 1)
  )
    .mul(sqft)
    .toNumber();
  const reserves = new Decimal(assumptions.reservesPerSqFt).mul(sqft).toNumber();
  const mgmtFee = new Decimal(grossRent)
    .mul(assumptions.managementFeePct)
    .toNumber();

  const noi = new Decimal(grossRent)
    .minus(nonTaxOpEx)
    .minus(propertyTax)
    .minus(reserves)
    .minus(mgmtFee)
    .toNumber();

  return {
    noi: money(noi),
    grossRent: money(grossRent),
    propertyTax: money(propertyTax),
    nonTaxOpEx: money(nonTaxOpEx),
  };
}

export function analyzeBuy(
  subject: SubjectProperty,
  market: MarketDerivation,
  assumptions: AnalysisAssumptions
): BuyAnalysis {
  const N = assumptions.holdingPeriodYears;
  const sqft = subject.buildingSqFt;

  const purchasePrice = money(market.derivedPurchasePrice);
  const closingCosts = money(purchasePrice * assumptions.closingCostPct);
  const loanAmount = money(purchasePrice * assumptions.ltv);
  const equity = money(purchasePrice - loanAmount);
  const upfrontCost = money(equity + closingCosts);

  const annualDebtService = annualMortgagePayment(
    loanAmount,
    assumptions.interestRate,
    assumptions.amortizationYears
  );
  const schedule = amortizationSchedule(
    loanAmount,
    assumptions.interestRate,
    assumptions.amortizationYears,
    N
  );

  const entryCapRate = market.avgAdjustedCapRate;
  const exitCapRate = entryCapRate + assumptions.exitCapPremium;

  const depreciation = money(
    (purchasePrice * assumptions.buildingValuePct) /
      assumptions.depreciationLifeYears
  );

  const cashFlows: YearlyBuyCashFlow[] = [];
  const annualOwnershipCost: number[] = [];

  for (let year = 1; year <= N; year++) {
    const { noi, grossRent, propertyTax, nonTaxOpEx } = noiForYear(
      subject,
      market,
      assumptions,
      year
    );
    const amort = schedule[year - 1];
    const interestPortion = amort.interest;
    const principalPortion = amort.principal;
    const taxShield = money(
      (depreciation + interestPortion) * assumptions.marginalTaxRate
    );
    const operatingCashFlow = money(noi - annualDebtService);
    const netCashFlow = money(operatingCashFlow + taxShield);

    cashFlows.push({
      year,
      noi,
      debtService: annualDebtService,
      interestPortion,
      principalPortion,
      depreciation,
      taxShield,
      propertyTax,
      operatingCashFlow,
      netCashFlow,
      loanBalanceEnd: amort.balanceEnd,
    });

    const reserves = money(assumptions.reservesPerSqFt * sqft);
    const mgmtFee = money(grossRent * assumptions.managementFeePct);
    const ownershipCost = money(
      annualDebtService +
        nonTaxOpEx +
        propertyTax +
        reserves +
        mgmtFee -
        taxShield
    );
    annualOwnershipCost.push(ownershipCost);
  }

  // ----- Terminal value -----
  const yearAfter = noiForYear(subject, market, assumptions, N + 1);
  const terminalValue = money(yearAfter.noi / exitCapRate);
  const sellingCosts = money(terminalValue * assumptions.sellingCostPct);
  const mortgagePayoff = schedule[N - 1].balanceEnd;

  const accumulatedDepreciation = money(depreciation * N);
  const appreciationGain = Math.max(terminalValue - purchasePrice, 0);
  const capitalGainsTax = money(appreciationGain * assumptions.capitalGainsRate);
  const recaptureTax = money(
    accumulatedDepreciation * assumptions.depreciationRecaptureRate
  );

  const netSaleProceeds = money(
    terminalValue -
      sellingCosts -
      mortgagePayoff -
      capitalGainsTax -
      recaptureTax
  );

  // ----- Investment cash-flow vector -----
  const investmentCashFlowVector: number[] = [-upfrontCost];
  cashFlows.forEach((cf, i) => {
    let net = cf.netCashFlow;
    if (i === N - 1) net = money(net + netSaleProceeds);
    investmentCashFlowVector.push(net);
  });

  const computedIrr = irr(investmentCashFlowVector);
  const computedNpv = npv(assumptions.discountRate, investmentCashFlowVector);

  return {
    purchasePrice,
    closingCosts,
    loanAmount,
    equity,
    annualDebtService,
    entryCapRate,
    exitCapRate,
    terminalValue,
    netSaleProceeds,
    cashFlows,
    investmentCashFlowVector,
    irr: computedIrr,
    npv: computedNpv,
    annualOwnershipCost,
    upfrontCost,
  };
}
