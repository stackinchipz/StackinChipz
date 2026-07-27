/**
 * Sensitivity analysis: how does the NPV advantage of buying move as we flex
 * the three assumptions that dominate the outcome — Exit Cap Rate, Discount
 * Rate, and property Tax Growth Rate?
 *
 * We emit one table per tax-growth scenario; each table is an
 * [exitCap x discountRate] grid of NPV-advantage-of-buying cells.
 */
import {
  AnalysisAssumptions,
  MarketDerivation,
  SensitivityCell,
  SensitivityTable,
  SubjectProperty,
} from '../types';
import { compare } from './comparisonEngine';

export interface SensitivityConfig {
  exitCapRates: number[];
  discountRates: number[];
  taxGrowthRates: number[];
}

/** Build a default grid centered on the base-case assumptions. */
export function defaultSensitivityConfig(
  base: AnalysisAssumptions,
  baseExitCap: number
): SensitivityConfig {
  const span = (center: number, step: number) => [
    Math.max(center - 2 * step, 0.0001),
    Math.max(center - step, 0.0001),
    center,
    center + step,
    center + 2 * step,
  ];
  return {
    exitCapRates: span(baseExitCap, 0.005).map((r) => Number(r.toFixed(4))),
    discountRates: span(base.discountRate, 0.01).map((r) => Number(r.toFixed(4))),
    taxGrowthRates: [0.0, base.taxGrowthRate, base.taxGrowthRate * 2].map((r) =>
      Number(r.toFixed(4))
    ),
  };
}

export function runSensitivity(
  subject: SubjectProperty,
  market: MarketDerivation,
  base: AnalysisAssumptions,
  config: SensitivityConfig
): SensitivityTable[] {
  const tables: SensitivityTable[] = [];

  for (const taxGrowthRate of config.taxGrowthRates) {
    const cells: SensitivityCell[] = [];
    for (const exitCapRate of config.exitCapRates) {
      for (const discountRate of config.discountRates) {
        // Override the exit cap by deriving the premium relative to entry cap.
        const exitCapPremium = exitCapRate - market.avgAdjustedCapRate;
        const assumptions: AnalysisAssumptions = {
          ...base,
          discountRate,
          taxGrowthRate,
          exitCapPremium,
        };
        const result = compare(subject, market, assumptions);
        cells.push({
          exitCapRate,
          discountRate,
          taxGrowthRate,
          npvAdvantageOfBuying: result.npvAdvantageOfBuying,
        });
      }
    }
    tables.push({
      taxGrowthRate,
      exitCapRates: config.exitCapRates,
      discountRates: config.discountRates,
      cells,
    });
  }

  return tables;
}
