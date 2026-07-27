/**
 * Pure financial primitives. No side effects, no I/O.
 *
 * decimal.js is used for the money-sensitive accumulations (amortization,
 * NPV) so we don't bleed floating-point error across a 10-year hold.
 */
import Decimal from 'decimal.js';

Decimal.set({ precision: 28, rounding: Decimal.ROUND_HALF_UP });

/** Round a number to cents. */
export function money(n: Decimal.Value): number {
  return new Decimal(n).toDecimalPlaces(2).toNumber();
}

/** Round to a fixed number of decimal places. */
export function round(n: Decimal.Value, dp = 6): number {
  return new Decimal(n).toDecimalPlaces(dp).toNumber();
}

/**
 * Level mortgage payment (annual) for a fully-amortizing loan.
 * Returns a positive number representing the annual debt service.
 */
export function annualMortgagePayment(
  principal: number,
  annualRate: number,
  amortYears: number
): number {
  const P = new Decimal(principal);
  if (P.lte(0)) return 0;
  const r = new Decimal(annualRate);
  if (r.lte(0)) return money(P.div(amortYears));
  const n = amortYears;
  const onePlusR = r.plus(1);
  const factor = onePlusR.pow(n);
  // P * r * (1+r)^n / ((1+r)^n - 1)
  const payment = P.mul(r).mul(factor).div(factor.minus(1));
  return money(payment);
}

export interface AmortYear {
  year: number;
  interest: number;
  principal: number;
  balanceEnd: number;
}

/**
 * Annual amortization schedule. The annual payment is computed once; each year
 * we split it into interest (on the opening balance) and principal.
 */
export function amortizationSchedule(
  principal: number,
  annualRate: number,
  amortYears: number,
  throughYears: number
): AmortYear[] {
  const payment = annualMortgagePayment(principal, annualRate, amortYears);
  const r = new Decimal(annualRate);
  let balance = new Decimal(principal);
  const rows: AmortYear[] = [];
  for (let year = 1; year <= throughYears; year++) {
    const interest = balance.mul(r);
    let principalPaid = new Decimal(payment).minus(interest);
    if (principalPaid.gt(balance)) principalPaid = balance;
    balance = balance.minus(principalPaid);
    if (balance.lt(0)) balance = new Decimal(0);
    rows.push({
      year,
      interest: money(interest),
      principal: money(principalPaid),
      balanceEnd: money(balance),
    });
  }
  return rows;
}

/** Net present value of a cash-flow vector. cashFlows[0] is time 0. */
export function npv(rate: number, cashFlows: number[]): number {
  const r = new Decimal(rate);
  let acc = new Decimal(0);
  cashFlows.forEach((cf, t) => {
    acc = acc.plus(new Decimal(cf).div(r.plus(1).pow(t)));
  });
  return money(acc);
}

/** First derivative of NPV with respect to rate (for Newton's method). */
function npvDerivative(rate: number, cashFlows: number[]): number {
  const r = new Decimal(rate);
  let acc = new Decimal(0);
  cashFlows.forEach((cf, t) => {
    if (t === 0) return;
    acc = acc.minus(
      new Decimal(cf).mul(t).div(r.plus(1).pow(t + 1))
    );
  });
  return acc.toNumber();
}

/**
 * Internal rate of return. Newton's method with a bisection fallback so we
 * stay robust on awkward (non-conventional) cash-flow vectors.
 *
 * Returns NaN when no sign change exists (IRR undefined).
 */
export function irr(cashFlows: number[], guess = 0.1): number {
  const hasPos = cashFlows.some((c) => c > 0);
  const hasNeg = cashFlows.some((c) => c < 0);
  if (!hasPos || !hasNeg) return NaN;

  // Newton's method.
  let rate = guess;
  for (let i = 0; i < 100; i++) {
    const f = npv(rate, cashFlows);
    if (Math.abs(f) < 1e-6) return round(rate, 8);
    const d = npvDerivative(rate, cashFlows);
    if (d === 0 || !isFinite(d)) break;
    const next = rate - f / d;
    if (!isFinite(next) || next <= -0.9999) break;
    if (Math.abs(next - rate) < 1e-9) return round(next, 8);
    rate = next;
  }

  // Bisection fallback over a wide bracket.
  let lo = -0.9999;
  let hi = 10;
  let fLo = npv(lo, cashFlows);
  let fHi = npv(hi, cashFlows);
  if (fLo * fHi > 0) return NaN;
  for (let i = 0; i < 200; i++) {
    const mid = (lo + hi) / 2;
    const fMid = npv(mid, cashFlows);
    if (Math.abs(fMid) < 1e-6) return round(mid, 8);
    if (fLo * fMid < 0) {
      hi = mid;
      fHi = fMid;
    } else {
      lo = mid;
      fLo = fMid;
    }
  }
  return round((lo + hi) / 2, 8);
}

/** Future value of a single sum compounded annually. */
export function futureValue(present: number, rate: number, years: number): number {
  return money(new Decimal(present).mul(new Decimal(rate).plus(1).pow(years)));
}

/** Compound a per-period value forward by `years` at `rate`. */
export function grow(base: number, rate: number, years: number): number {
  return new Decimal(base).mul(new Decimal(rate).plus(1).pow(years)).toNumber();
}

/** Mean of a numeric array (0 for empty). */
export function mean(values: number[]): number {
  if (values.length === 0) return 0;
  const sum = values.reduce((a, b) => new Decimal(a).plus(b).toNumber(), 0);
  return sum / values.length;
}
