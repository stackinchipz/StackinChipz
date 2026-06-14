/**
 * Lease vs. Buy comparison. Pure functions.
 *
 * Produces the three headline metrics:
 *   1. NPV of Costs (Buy vs Lease)   — lower is better.
 *   2. Differential IRR              — return on the EXTRA capital buying ties
 *                                      up vs leasing. Beat the discount rate and
 *                                      buying wins.
 *   3. Break-even year               — when cumulative buy cash flow overtakes
 *                                      leasing.
 */
import {
  AnalysisAssumptions,
  BuyAnalysis,
  ComparisonResult,
  LeaseAnalysis,
  MarketDerivation,
  SubjectProperty,
} from '../types';
import { analyzeBuy } from './buyAnalyzer';
import { irr, money, npv } from './finance';
import { analyzeLease } from './leaseAnalyzer';

/** Cost cash-flow vector for the BUY scenario (positive = cost outflow). */
export function buyCostVector(buy: BuyAnalysis): number[] {
  const N = buy.annualOwnershipCost.length;
  const vec: number[] = [buy.upfrontCost];
  buy.annualOwnershipCost.forEach((oc, i) => {
    let cost = oc;
    // Year N: selling returns equity + appreciation, a large cost credit.
    if (i === N - 1) cost = money(cost - buy.netSaleProceeds);
    vec.push(cost);
  });
  return vec;
}

/** Incremental (buy - lease) cash flow used for the differential IRR. */
export function differentialCashFlow(
  buy: BuyAnalysis,
  lease: LeaseAnalysis
): number[] {
  const N = buy.annualOwnershipCost.length;
  // t0: buying ties up more cash upfront (negative = outflow vs leasing).
  const vec: number[] = [money(-(buy.upfrontCost - lease.upfrontCost))];
  for (let i = 0; i < N; i++) {
    // Each year buying "saves" the lease payment but pays ownership costs.
    let cf = money(lease.annualLeaseCost[i] - buy.annualOwnershipCost[i]);
    if (i === N - 1) cf = money(cf + buy.netSaleProceeds);
    vec.push(cf);
  }
  return vec;
}

/** First year cumulative differential cash flow turns non-negative. */
export function breakEvenYear(differential: number[]): number | null {
  let cumulative = 0;
  for (let t = 0; t < differential.length; t++) {
    cumulative += differential[t];
    if (t > 0 && cumulative >= 0) return t;
  }
  return null;
}

export function compare(
  subject: SubjectProperty,
  market: MarketDerivation,
  assumptions: AnalysisAssumptions
): ComparisonResult {
  const buy = analyzeBuy(subject, market, assumptions);
  const lease = analyzeLease(subject, market, assumptions, {
    investableEquity: buy.upfrontCost,
  });

  const buyNpvCost = npv(assumptions.discountRate, buyCostVector(buy));
  const leaseNpvCost = lease.npvCost;
  const npvAdvantageOfBuying = money(leaseNpvCost - buyNpvCost);

  const differential = differentialCashFlow(buy, lease);
  const differentialIrr = irr(differential);
  const beYear = breakEvenYear(differential);

  const { recommendation, rationale } = recommend(
    buyNpvCost,
    leaseNpvCost,
    differentialIrr,
    assumptions.discountRate,
    beYear,
    assumptions.holdingPeriodYears
  );

  return {
    buy,
    lease,
    buyNpvCost,
    leaseNpvCost,
    npvAdvantageOfBuying,
    differentialIrr,
    breakEvenYear: beYear,
    recommendation,
    rationale,
  };
}

export function recommend(
  buyNpvCost: number,
  leaseNpvCost: number,
  differentialIrr: number,
  discountRate: number,
  beYear: number | null,
  holdingPeriod: number
): { recommendation: 'BUY' | 'LEASE' | 'TOSS_UP'; rationale: string } {
  const denom = Math.max(Math.abs(leaseNpvCost), 1);
  const advantagePct = (leaseNpvCost - buyNpvCost) / denom;
  const irrBeatsHurdle = isFinite(differentialIrr) && differentialIrr > discountRate;

  let recommendation: 'BUY' | 'LEASE' | 'TOSS_UP';
  if (advantagePct > 0.02 && irrBeatsHurdle) {
    recommendation = 'BUY';
  } else if (advantagePct < -0.02) {
    recommendation = 'LEASE';
  } else {
    recommendation = 'TOSS_UP';
  }

  const irrStr = isFinite(differentialIrr)
    ? `${(differentialIrr * 100).toFixed(1)}%`
    : 'n/a';
  const beStr =
    beYear != null ? `year ${beYear}` : `not within ${holdingPeriod}-yr hold`;

  const rationale =
    `Buy NPV cost $${Math.round(buyNpvCost).toLocaleString()} vs Lease NPV cost ` +
    `$${Math.round(leaseNpvCost).toLocaleString()} ` +
    `(buying ${advantagePct >= 0 ? 'saves' : 'costs'} ` +
    `${Math.abs(advantagePct * 100).toFixed(1)}%). ` +
    `Differential IRR ${irrStr} vs ${(discountRate * 100).toFixed(1)}% hurdle. ` +
    `Break-even ${beStr}.`;

  return { recommendation, rationale };
}
