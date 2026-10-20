/**
 * Top-level analysis orchestrator. Wires the comp selector, the buy/lease
 * analyzers, the comparison engine and the sensitivity grid into a single
 * {@link AnalysisResult}.
 */
import {
  AnalysisAssumptions,
  AnalysisResult,
  LeaseComp,
  SaleComp,
  SubjectProperty,
} from '../types';
import { compare } from './comparisonEngine';
import {
  deriveMarket,
  selectLeaseComps,
  selectSaleComps,
} from './compSelector';
import {
  defaultSensitivityConfig,
  runSensitivity,
  SensitivityConfig,
} from './sensitivity';

/** Sensible US-market defaults. Every value is overridable via the CLI. */
export const DEFAULT_ASSUMPTIONS: AnalysisAssumptions = {
  holdingPeriodYears: 10,
  discountRate: 0.08,
  ltv: 0.7,
  interestRate: 0.065,
  amortizationYears: 25,
  closingCostPct: 0.025,
  exitCapPremium: 0.0075,
  sellingCostPct: 0.05,
  rentGrowthRate: 0.03,
  taxGrowthRate: 0.02,
  reservesPerSqFt: 0.15,
  managementFeePct: 0.03,
  marginalTaxRate: 0.35,
  capitalGainsRate: 0.2,
  depreciationRecaptureRate: 0.25,
  buildingValuePct: 0.8,
  depreciationLifeYears: 39,
  leaseLegalBrokerPerSqFt: 0.5,
  movingCostPerSqFt: 2.0,
  opportunityCostRate: 0.07,
};

export interface RunAnalysisInput {
  subject: SubjectProperty;
  saleComps: SaleComp[];
  leaseComps: LeaseComp[];
  assumptions?: Partial<AnalysisAssumptions>;
  sensitivityConfig?: SensitivityConfig;
  /** Skip the (expensive) sensitivity grid. */
  skipSensitivity?: boolean;
}

export function runAnalysis(input: RunAnalysisInput): AnalysisResult {
  const assumptions: AnalysisAssumptions = {
    ...DEFAULT_ASSUMPTIONS,
    ...(input.assumptions ?? {}),
  };

  // Depreciation life follows asset class unless explicitly overridden.
  if (input.assumptions?.depreciationLifeYears == null) {
    assumptions.depreciationLifeYears =
      input.subject.propertyType === 'multifamily' ? 27.5 : 39;
  }

  const saleComps = selectSaleComps(input.subject, input.saleComps);
  const leaseComps = selectLeaseComps(input.subject, input.leaseComps);
  const market = deriveMarket(input.subject, saleComps, leaseComps);

  const comparison = compare(input.subject, market, assumptions);

  const sensitivity = input.skipSensitivity
    ? []
    : runSensitivity(
        input.subject,
        market,
        assumptions,
        input.sensitivityConfig ??
          defaultSensitivityConfig(assumptions, comparison.buy.exitCapRate)
      );

  return {
    subject: input.subject,
    assumptions,
    market,
    comparison,
    sensitivity,
    generatedAt: new Date().toISOString(),
  };
}
