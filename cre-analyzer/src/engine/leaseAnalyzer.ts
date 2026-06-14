/**
 * LEASE scenario (tenant). Pure functions.
 *
 * The market rent we use is the tax-normalized, NNN-equivalent all-in
 * occupancy cost derived from the lease comps (see compSelector). Because every
 * comp was collapsed to an all-in number at the SUBJECT's tax, the tenant's
 * lease payment already includes its share of property tax — exactly the
 * apples-to-apples basis the engine requires.
 */
import Decimal from 'decimal.js';
import {
  AnalysisAssumptions,
  LeaseAnalysis,
  MarketDerivation,
  SubjectProperty,
  YearlyLeaseCashFlow,
} from '../types';
import { grow, money, npv } from './finance';

export interface LeaseOptions {
  /**
   * The equity a buyer would have tied up (buy upfront cost). Used only to
   * surface the informational "opportunity gain" of leasing instead of buying;
   * it does NOT feed the NPV-of-cost vector (the discount rate already prices
   * the cost of capital).
   */
  investableEquity?: number;
  /** Months of free rent at lease commencement. */
  freeRentMonths?: number;
}

export function analyzeLease(
  subject: SubjectProperty,
  market: MarketDerivation,
  assumptions: AnalysisAssumptions,
  options: LeaseOptions = {}
): LeaseAnalysis {
  const N = assumptions.holdingPeriodYears;
  const sqft = subject.buildingSqFt;
  const marketRentPerSqFt = market.avgSubjectAdjustedRent;
  const freeRentMonths = options.freeRentMonths ?? 0;

  // Upfront: legal/broker + moving, offset by TI allowance.
  const tiOffset = money(0); // subject lease TI is a market concession; modeled as 0 unless supplied
  const legalBroker = money(assumptions.leaseLegalBrokerPerSqFt * sqft);
  const moving = money(assumptions.movingCostPerSqFt * sqft);
  const upfrontCost = money(legalBroker + moving - tiOffset);

  const cashFlows: YearlyLeaseCashFlow[] = [];
  const costCashFlowVector: number[] = [upfrontCost];
  const annualLeaseCost: number[] = [];

  for (let year = 1; year <= N; year++) {
    const rentPerSqFt = grow(
      marketRentPerSqFt,
      assumptions.rentGrowthRate,
      year - 1
    );
    const baseRent = new Decimal(rentPerSqFt).mul(sqft).toNumber();

    // Free rent applies only in year 1, prorated by months.
    const freeRentCredit =
      year === 1
        ? new Decimal(baseRent).mul(freeRentMonths).div(12).toNumber()
        : 0;

    const leasePayment = money(baseRent - freeRentCredit);
    const opportunityGain = money(
      (options.investableEquity ?? 0) * assumptions.opportunityCostRate
    );

    cashFlows.push({
      year,
      baseRent: money(baseRent),
      // All-in market rent already bundles the tenant's OpEx reimbursement.
      opExReimbursement: 0,
      freeRentCredit: money(freeRentCredit),
      leasePayment,
      opportunityGain,
    });

    costCashFlowVector.push(leasePayment);
    annualLeaseCost.push(leasePayment);
  }

  const npvCost = npv(assumptions.discountRate, costCashFlowVector);

  return {
    marketRentPerSqFt,
    upfrontCost,
    tiOffset,
    cashFlows,
    costCashFlowVector,
    npvCost,
    annualLeaseCost,
  };
}
