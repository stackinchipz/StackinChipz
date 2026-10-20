/**
 * Property-tax normalization engine — the heart of the tool.
 *
 * THE PROBLEM: comps are quoted under *their own* tax reality, not the
 * subject's. A sale comp's NOI reflects the seller's (often stale, low)
 * assessed value. A lease comp's quote bundles property tax differently
 * depending on lease structure (NNN vs Gross) and the comp's tax jurisdiction.
 * Comparing them directly is apples-to-oranges.
 *
 * THE FIX: restate every comp at the SUBJECT property's projected tax burden.
 *   - Sale comps: strip the comp's old tax out of NOI, inject the subject's
 *     projected post-sale tax, then recompute the cap rate.
 *   - Lease comps: collapse every lease structure to an all-in NNN-equivalent
 *     occupancy cost, then swap the comp's embedded tax for the subject's.
 *
 * All functions here are PURE.
 */
import Decimal from 'decimal.js';
import {
  BaseComp,
  LeaseComp,
  NormalizedComp,
  NormalizedLeaseComp,
  NormalizedSaleComp,
  PropertyTaxContext,
  SaleComp,
} from '../types';
import { round } from './finance';

/** The subject's projected post-sale tax expressed as $/SF/yr. */
export function subjectProjectedTaxPerSqFt(
  subjectTax: PropertyTaxContext,
  subjectSqFt: number
): number {
  if (subjectSqFt <= 0) return subjectTax.taxRatePerSqFt;
  return new Decimal(subjectTax.estimatedPostTransactionTax)
    .div(subjectSqFt)
    .toNumber();
}

/**
 * Project the Year-1 tax bill for the subject IF it is purchased today.
 *
 * When the assessment is sale-triggered and we know the jurisdiction's millage
 * and assessment ratio, the new bill is `salePrice * ratio * millage`. A
 * statutory cap (Prop 13 CA, FL 2%, etc.) limits how far the *assessed value*
 * can jump relative to the prior assessment in a non-sale year — but a sale
 * itself resets the basis, so caps apply to subsequent years, not Year 1.
 */
export function projectPostSaleTax(
  tax: PropertyTaxContext,
  salePrice: number
): number {
  if (tax.reassessmentTrigger === 'none') {
    return tax.annualTaxAmount;
  }
  const ratio = tax.assessmentRatio ?? 1;
  const millage = tax.millageRate;
  if (tax.reassessmentValueBasis === 'sale_price' && millage != null) {
    return new Decimal(salePrice).mul(ratio).mul(millage).toNumber();
  }
  // No millage info — fall back to the supplied estimate.
  return tax.estimatedPostTransactionTax;
}

/**
 * Apply a statutory assessed-value growth cap year over year.
 * Returns the capped tax for `yearsForward` years after the assessment reset.
 */
export function applyAssessmentCap(
  baseTax: number,
  cap: number | undefined,
  yearsForward: number,
  uncappedGrowth: number
): number {
  if (yearsForward <= 0) return baseTax;
  const effectiveGrowth = cap == null ? uncappedGrowth : Math.min(cap, uncappedGrowth);
  return new Decimal(baseTax)
    .mul(new Decimal(1 + effectiveGrowth).pow(yearsForward))
    .toNumber();
}

/**
 * Normalize a SALE comp to the subject's tax burden.
 *
 * The reported NOI is post-(comp)tax. To restate it under the subject's tax we
 * add the comp's own tax back, then subtract the subject's projected tax
 * (scaled to the comp's building size):
 *
 *   adjustedNoi = reportedNoi + oldTax - newProjectedTax
 *
 * Note: the prompt's shorthand "Reported NOI - Old Tax + New" assumes NOI is
 * quoted *pre*-tax; our NOI is post-tax (per the type contract), so the signs
 * flip. Either way the economics are identical and match the validation
 * requirement: a higher subject tax must DROP the adjusted cap rate.
 */
export function normalizeSaleComp(
  comp: SaleComp,
  subjectTax: PropertyTaxContext,
  subjectSqFt: number
): NormalizedSaleComp {
  const reportedNoi = comp.noi;
  const oldAnnualTax = comp.taxContext.annualTaxAmount;

  const subjTaxPerSqFt = subjectProjectedTaxPerSqFt(subjectTax, subjectSqFt);
  const newProjectedTax = new Decimal(subjTaxPerSqFt)
    .mul(comp.buildingSqFt)
    .toNumber();

  const adjustedNoi = new Decimal(reportedNoi)
    .plus(oldAnnualTax)
    .minus(newProjectedTax)
    .toNumber();

  const reportedCapRate =
    comp.salePrice > 0
      ? new Decimal(reportedNoi).div(comp.salePrice).toNumber()
      : 0;
  const adjustedCapRate =
    comp.salePrice > 0
      ? new Decimal(adjustedNoi).div(comp.salePrice).toNumber()
      : 0;

  return {
    comp,
    reportedNoi: round(reportedNoi, 2),
    oldAnnualTax: round(oldAnnualTax, 2),
    newProjectedTax: round(newProjectedTax, 2),
    adjustedNoi: round(adjustedNoi, 2),
    adjustedCapRate: round(adjustedCapRate, 6),
    reportedCapRate: round(reportedCapRate, 6),
    pricePerSqFt: round(comp.pricePerSqFt, 2),
  };
}

/**
 * Total all-in occupancy cost ($/SF/yr) a tenant bears under a given lease
 * structure, expressed at the comp's OWN tax level. This is the "NNN
 * equivalent": every structure is collapsed to a single comparable number.
 *
 *   NNN : base + tax + insurance + cam               (tenant pays all OpEx)
 *   NN  : base + tax + insurance                     (CAM embedded in base)
 *   N   : base + tax                                 (ins + CAM embedded)
 *   Gross: base                                      (all OpEx embedded)
 *   Modified Gross: base + (tenant share over stop)  (rest embedded in base)
 *
 * In every case the property tax is *somewhere* in the all-in cost — either an
 * explicit pass-through or embedded in a grossed-up base rent. That is exactly
 * what lets us swap it for the subject's tax in {@link normalizeLeaseComp}.
 */
export function nnnEquivalentRent(comp: LeaseComp): number {
  const base = new Decimal(comp.leaseRatePerSqFtYr);
  const { propertyTax, insurance, cam } = comp.opExBreakdown;
  switch (comp.leaseType) {
    case 'NNN':
      return base.plus(propertyTax).plus(insurance).plus(cam).toNumber();
    case 'NN':
      return base.plus(propertyTax).plus(insurance).toNumber();
    case 'N':
      return base.plus(propertyTax).toNumber();
    case 'Gross':
      // Base is already grossed-up to cover all OpEx incl. tax.
      return base.toNumber();
    case 'Modified Gross': {
      // Tenant pays the share of OpEx above the base-year expense stop.
      const stop = comp.expenseStopPerSqFt ?? comp.opExBreakdown.totalOpEx;
      const tenantShare = Decimal.max(
        new Decimal(comp.opExBreakdown.totalOpEx).minus(stop),
        0
      );
      return base.plus(tenantShare).toNumber();
    }
    default:
      return base.toNumber();
  }
}

/**
 * The property-tax component ($/SF/yr) that is embedded in (or passed through
 * on top of) a comp's all-in occupancy cost. For NNN/NN/N this is the quoted
 * pass-through; for Gross/Modified-Gross it is imputed from the comp's own tax
 * context (taxRatePerSqFt), since the tax is buried inside the base rent.
 */
export function embeddedTaxPerSqFt(comp: LeaseComp): number {
  switch (comp.leaseType) {
    case 'NNN':
    case 'NN':
    case 'N':
      return comp.opExBreakdown.propertyTax;
    case 'Gross':
    case 'Modified Gross':
    default:
      // Impute from the comp's tax jurisdiction.
      return comp.taxContext.taxRatePerSqFt || comp.opExBreakdown.propertyTax;
  }
}

/**
 * Normalize a LEASE comp to the subject's tax burden.
 *
 *   nnnEquivalent      = all-in occupancy cost at the comp's tax
 *   subjectAdjusted    = nnnEquivalent - compTax + subjectTax
 *
 * Swapping the tax component restates the comp as if it sat under the subject's
 * tax bill, so a $15 Gross lease in a low-tax county and a $15 NNN bundle in a
 * high-tax county no longer look identical.
 */
export function normalizeLeaseComp(
  comp: LeaseComp,
  subjectTax: PropertyTaxContext,
  subjectSqFt: number
): NormalizedLeaseComp {
  const nnnEquiv = nnnEquivalentRent(comp);
  const compTaxPerSqFt = embeddedTaxPerSqFt(comp);
  const subjectTaxPerSqFt = subjectProjectedTaxPerSqFt(subjectTax, subjectSqFt);

  const subjectAdjustedRent = new Decimal(nnnEquiv)
    .minus(compTaxPerSqFt)
    .plus(subjectTaxPerSqFt)
    .toNumber();

  return {
    comp,
    nnnEquivalentRent: round(nnnEquiv, 4),
    subjectAdjustedRent: round(subjectAdjustedRent, 4),
    compTaxPerSqFt: round(compTaxPerSqFt, 4),
    subjectTaxPerSqFt: round(subjectTaxPerSqFt, 4),
  };
}

/**
 * Generic entry point. Dispatches to the sale/lease normalizer based on the
 * shape of the comp, returning a discriminated union.
 */
export function normalizeTaxes(
  comp: BaseComp,
  subjectTax: PropertyTaxContext,
  subjectSqFt: number
): NormalizedComp {
  if (isSaleComp(comp)) {
    return { kind: 'sale', ...normalizeSaleComp(comp, subjectTax, subjectSqFt) };
  }
  if (isLeaseComp(comp)) {
    return { kind: 'lease', ...normalizeLeaseComp(comp, subjectTax, subjectSqFt) };
  }
  throw new Error(`Comp ${comp.id} is neither a sale nor a lease comp.`);
}

export function isSaleComp(comp: BaseComp): comp is SaleComp {
  return (comp as SaleComp).salePrice != null;
}

export function isLeaseComp(comp: BaseComp): comp is LeaseComp {
  return (comp as LeaseComp).leaseRatePerSqFtYr != null;
}
