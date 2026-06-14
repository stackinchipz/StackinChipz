import {
  applyAssessmentCap,
  embeddedTaxPerSqFt,
  nnnEquivalentRent,
  normalizeLeaseComp,
  normalizeSaleComp,
  normalizeTaxes,
  projectPostSaleTax,
  subjectProjectedTaxPerSqFt,
} from '../src/engine/taxNormalizer';
import {
  LeaseComp,
  PropertyTaxContext,
  SaleComp,
} from '../src/types';

function taxCtx(ratePerSqFt: number, sqft: number, over: Partial<PropertyTaxContext> = {}): PropertyTaxContext {
  return {
    annualTaxAmount: ratePerSqFt * sqft,
    taxRatePerSqFt: ratePerSqFt,
    assessmentYear: 2022,
    reassessmentTrigger: 'sale',
    reassessmentValueBasis: 'sale_price',
    estimatedPostTransactionTax: ratePerSqFt * sqft,
    ...over,
  };
}

function saleComp(over: Partial<SaleComp> = {}): SaleComp {
  return {
    id: 'S',
    address: 'x',
    propertyType: 'industrial',
    buildingSqFt: 10000,
    landAcres: 1,
    yearBuilt: 2005,
    salePrice: 1_000_000,
    saleDate: '2025-01-01',
    noi: 70_000,
    pricePerSqFt: 100,
    capRate: 0.07,
    taxContext: taxCtx(0.5, 10000),
    ...over,
  };
}

function leaseComp(over: Partial<LeaseComp> = {}): LeaseComp {
  return {
    id: 'L',
    address: 'x',
    propertyType: 'industrial',
    buildingSqFt: 10000,
    landAcres: 1,
    yearBuilt: 2005,
    leaseRatePerSqFtYr: 10,
    leaseType: 'NNN',
    opExBreakdown: { propertyTax: 3, insurance: 1, cam: 1, totalOpEx: 5 },
    effectiveRentPerSqFt: 15,
    leaseTermYears: 5,
    tenantImprovementAllowance: 0,
    freeRentMonths: 0,
    escalations: [],
    taxContext: taxCtx(3, 10000),
    ...over,
  };
}

describe('subjectProjectedTaxPerSqFt', () => {
  it('derives $/SF from the total post-transaction bill', () => {
    const ctx = taxCtx(1.5, 20000, { estimatedPostTransactionTax: 40000 });
    expect(subjectProjectedTaxPerSqFt(ctx, 20000)).toBeCloseTo(2.0, 6);
  });

  it('falls back to current rate when SF is unknown', () => {
    const ctx = taxCtx(1.5, 20000);
    expect(subjectProjectedTaxPerSqFt(ctx, 0)).toBe(1.5);
  });
});

describe('normalizeSaleComp — reassessment to a higher subject tax', () => {
  // Validation checklist: comp tax $0.50/SF, subject projected $2.00/SF =>
  // adjusted cap rate must drop significantly.
  it('drops the adjusted cap rate when subject tax is much higher', () => {
    const comp = saleComp(); // 10k SF, $0.50/SF tax, $70k NOI, $1M price => 7% cap
    const subjectTax = taxCtx(1.5, 10000, { estimatedPostTransactionTax: 20000 }); // $2.00/SF
    const n = normalizeSaleComp(comp, subjectTax, 10000);

    expect(n.oldAnnualTax).toBe(5000);
    expect(n.newProjectedTax).toBe(20000);
    expect(n.adjustedNoi).toBe(55000); // 70k + 5k - 20k
    expect(n.reportedCapRate).toBeCloseTo(0.07, 6);
    expect(n.adjustedCapRate).toBeCloseTo(0.055, 6);
    expect(n.adjustedCapRate).toBeLessThan(n.reportedCapRate - 0.01);
  });

  it('raises the adjusted cap rate when subject tax is lower', () => {
    const comp = saleComp({ taxContext: taxCtx(2.0, 10000) }); // $2/SF, $20k tax baked in
    const subjectTax = taxCtx(0.5, 10000, { estimatedPostTransactionTax: 5000 }); // $0.50/SF
    const n = normalizeSaleComp(comp, subjectTax, 10000);
    expect(n.adjustedNoi).toBe(85000); // 70k + 20k - 5k
    expect(n.adjustedCapRate).toBeGreaterThan(n.reportedCapRate);
  });
});

describe('nnnEquivalentRent — collapse every lease structure', () => {
  it('NNN: base + tax + ins + cam', () => {
    expect(nnnEquivalentRent(leaseComp())).toBeCloseTo(15, 6);
  });

  it('Gross: base already all-in', () => {
    const gross = leaseComp({ leaseType: 'Gross', leaseRatePerSqFtYr: 15 });
    expect(nnnEquivalentRent(gross)).toBeCloseTo(15, 6);
  });

  it('NN: base + tax + ins (CAM embedded)', () => {
    const nn = leaseComp({ leaseType: 'NN', leaseRatePerSqFtYr: 11 });
    expect(nnnEquivalentRent(nn)).toBeCloseTo(11 + 3 + 1, 6);
  });

  it('N: base + tax only', () => {
    const n = leaseComp({ leaseType: 'N', leaseRatePerSqFtYr: 13 });
    expect(nnnEquivalentRent(n)).toBeCloseTo(13 + 3, 6);
  });

  it('Modified Gross: base + OpEx above the expense stop', () => {
    const mg = leaseComp({
      leaseType: 'Modified Gross',
      leaseRatePerSqFtYr: 12.5,
      opExBreakdown: { propertyTax: 1.4, insurance: 0.45, cam: 0.65, totalOpEx: 2.5 },
      expenseStopPerSqFt: 2.0,
    });
    // tenant pays 2.5 - 2.0 = 0.5 over stop
    expect(nnnEquivalentRent(mg)).toBeCloseTo(13.0, 6);
  });
});

describe('Gross vs NNN normalization parity (validation checklist)', () => {
  it('a $15 Gross and a $10+$3+$1+$1 NNN both land at ~$15 effective', () => {
    const subjectTax = taxCtx(3, 10000); // subject $3/SF so no tax shift
    const nnn = normalizeLeaseComp(leaseComp(), subjectTax, 10000);
    const gross = normalizeLeaseComp(
      leaseComp({ leaseType: 'Gross', leaseRatePerSqFtYr: 15, taxContext: taxCtx(3, 10000) }),
      subjectTax,
      10000
    );
    expect(nnn.subjectAdjustedRent).toBeCloseTo(15, 4);
    expect(gross.subjectAdjustedRent).toBeCloseTo(15, 4);
  });

  it('a high-tax Gross and a low-tax NNN diverge once normalized', () => {
    // $15 Gross in a $4/SF tax county vs $15 NNN bundle in a $1/SF county.
    const subjectTax = taxCtx(2, 10000); // subject sits at $2/SF
    const grossHighTax = normalizeLeaseComp(
      leaseComp({ leaseType: 'Gross', leaseRatePerSqFtYr: 15, taxContext: taxCtx(4, 10000) }),
      subjectTax,
      10000
    );
    const nnnLowTax = normalizeLeaseComp(
      leaseComp({
        leaseRatePerSqFtYr: 13,
        opExBreakdown: { propertyTax: 1, insurance: 0.5, cam: 0.5, totalOpEx: 2 },
        taxContext: taxCtx(1, 10000),
      }),
      subjectTax,
      10000
    );
    // Gross: 15 - 4 + 2 = 13 ; NNN: 15 - 1 + 2 = 16  -> they are NOT equal.
    expect(grossHighTax.subjectAdjustedRent).toBeCloseTo(13, 4);
    expect(nnnLowTax.subjectAdjustedRent).toBeCloseTo(16, 4);
    expect(grossHighTax.subjectAdjustedRent).not.toBeCloseTo(
      nnnLowTax.subjectAdjustedRent,
      1
    );
  });
});

describe('embeddedTaxPerSqFt', () => {
  it('uses the pass-through for net leases', () => {
    expect(embeddedTaxPerSqFt(leaseComp())).toBe(3);
  });
  it('imputes from tax context for gross leases', () => {
    const gross = leaseComp({ leaseType: 'Gross', taxContext: taxCtx(2.7, 10000) });
    expect(embeddedTaxPerSqFt(gross)).toBe(2.7);
  });
});

describe('projectPostSaleTax — sale-triggered reassessment', () => {
  it('computes new bill from sale price * ratio * millage', () => {
    const ctx = taxCtx(1.0, 20000, {
      reassessmentTrigger: 'sale',
      reassessmentValueBasis: 'sale_price',
      millageRate: 0.0222,
      assessmentRatio: 1.0,
    });
    expect(projectPostSaleTax(ctx, 3_600_000)).toBeCloseTo(79920, 0);
  });

  it('returns current bill when there is no reassessment trigger', () => {
    const ctx = taxCtx(1.0, 20000, { reassessmentTrigger: 'none', annualTaxAmount: 20000 });
    expect(projectPostSaleTax(ctx, 5_000_000)).toBe(20000);
  });
});

describe('applyAssessmentCap — statutory caps (Prop 13 / FL 2%)', () => {
  it('caps annual growth at the statutory limit', () => {
    // Uncapped 5% growth but a 2% cap => use 2%.
    const capped = applyAssessmentCap(10000, 0.02, 3, 0.05);
    expect(capped).toBeCloseTo(10000 * 1.02 ** 3, 4);
  });

  it('uses uncapped growth when no cap is set', () => {
    const uncapped = applyAssessmentCap(10000, undefined, 2, 0.05);
    expect(uncapped).toBeCloseTo(10000 * 1.05 ** 2, 4);
  });

  it('is a no-op at year zero', () => {
    expect(applyAssessmentCap(10000, 0.02, 0, 0.05)).toBe(10000);
  });
});

describe('normalizeTaxes dispatch', () => {
  it('routes sale comps', () => {
    const r = normalizeTaxes(saleComp(), taxCtx(1, 10000), 10000);
    expect(r.kind).toBe('sale');
  });
  it('routes lease comps', () => {
    const r = normalizeTaxes(leaseComp(), taxCtx(1, 10000), 10000);
    expect(r.kind).toBe('lease');
  });
});
