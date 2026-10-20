/**
 * Subject-Property-Centric comp workflow.
 *
 * We never expect one address to be simultaneously listed for sale AND lease
 * with four comps each. Instead, standard appraisal methodology: take the
 * subject property, pull comparable SALES and comparable LEASES separately,
 * then normalize BOTH sets to the subject's own tax reality before deriving a
 * value. That normalization is what makes the two sets comparable.
 */
import {
  LeaseComp,
  MarketDerivation,
  SaleComp,
  SubjectProperty,
} from '../types';
import { mean } from './finance';
import {
  normalizeLeaseComp,
  normalizeSaleComp,
} from './taxNormalizer';

export interface CompSelectionOptions {
  /** Restrict to comps within +/- this fraction of subject building size. */
  sizeTolerance?: number;
  /** Restrict to comps within this many years of subject's age. */
  ageToleranceYears?: number;
  /** Required minimum of each comp type. */
  minComps?: number;
}

/**
 * Score a comp's similarity to the subject (lower is closer). Used to rank and
 * select the most comparable transactions when more than the minimum exist.
 */
export function similarityScore(
  subject: SubjectProperty,
  comp: { buildingSqFt: number; yearBuilt: number; propertyType: string }
): number {
  const sizeDelta =
    Math.abs(comp.buildingSqFt - subject.buildingSqFt) /
    Math.max(subject.buildingSqFt, 1);
  const ageDelta = Math.abs(comp.yearBuilt - subject.yearBuilt) / 50;
  const typePenalty = comp.propertyType === subject.propertyType ? 0 : 1;
  return sizeDelta + ageDelta + typePenalty;
}

export function selectSaleComps(
  subject: SubjectProperty,
  pool: SaleComp[],
  count = 4
): SaleComp[] {
  return [...pool]
    .sort((a, b) => similarityScore(subject, a) - similarityScore(subject, b))
    .slice(0, count);
}

export function selectLeaseComps(
  subject: SubjectProperty,
  pool: LeaseComp[],
  count = 4
): LeaseComp[] {
  return [...pool]
    .sort((a, b) => similarityScore(subject, a) - similarityScore(subject, b))
    .slice(0, count);
}

/**
 * Normalize the selected comps to the subject's tax context and derive the
 * market inputs the financial engine needs: an adjusted purchase price, an
 * adjusted cap rate, and an all-in market rent.
 */
export function deriveMarket(
  subject: SubjectProperty,
  saleComps: SaleComp[],
  leaseComps: LeaseComp[]
): MarketDerivation {
  const subjectSqFt = subject.buildingSqFt;

  const normalizedSales = saleComps.map((c) =>
    normalizeSaleComp(c, subject.taxContext, subjectSqFt)
  );
  const normalizedLeases = leaseComps.map((c) =>
    normalizeLeaseComp(c, subject.taxContext, subjectSqFt)
  );

  const avgAdjustedPricePerSqFt = mean(
    normalizedSales.map((s) => s.pricePerSqFt)
  );
  const avgAdjustedCapRate = mean(
    normalizedSales.map((s) => s.adjustedCapRate)
  );
  const avgSubjectAdjustedRent = mean(
    normalizedLeases.map((l) => l.subjectAdjustedRent)
  );

  // Non-tax OpEx (insurance + CAM) averaged across lease comps, $/SF/yr.
  const avgNonTaxOpExPerSqFt = mean(
    leaseComps.map(
      (l) => l.opExBreakdown.insurance + l.opExBreakdown.cam
    )
  );

  const derivedPurchasePrice = avgAdjustedPricePerSqFt * subjectSqFt;

  return {
    normalizedSales,
    normalizedLeases,
    avgAdjustedPricePerSqFt,
    avgAdjustedCapRate,
    avgSubjectAdjustedRent,
    avgNonTaxOpExPerSqFt,
    derivedPurchasePrice,
  };
}
