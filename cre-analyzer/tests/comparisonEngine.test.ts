import {
  breakEvenYear,
  compare,
  differentialCashFlow,
  recommend,
} from '../src/engine/comparisonEngine';
import { deriveMarket } from '../src/engine/compSelector';
import { DEFAULT_ASSUMPTIONS, runAnalysis } from '../src/engine/analysis';
import {
  MOCK_LEASE_COMPS,
  MOCK_SALE_COMPS,
  MOCK_SUBJECT,
} from '../src/providers/MockProvider';

const market = deriveMarket(MOCK_SUBJECT, MOCK_SALE_COMPS, MOCK_LEASE_COMPS);

describe('compare — mock industrial', () => {
  const result = compare(MOCK_SUBJECT, market, DEFAULT_ASSUMPTIONS);

  it('produces finite NPV costs for both scenarios', () => {
    expect(Number.isFinite(result.buyNpvCost)).toBe(true);
    expect(Number.isFinite(result.leaseNpvCost)).toBe(true);
  });

  it('npvAdvantageOfBuying = leaseNpvCost - buyNpvCost', () => {
    expect(result.npvAdvantageOfBuying).toBeCloseTo(
      result.leaseNpvCost - result.buyNpvCost,
      0
    );
  });

  it('emits a valid recommendation and rationale', () => {
    expect(['BUY', 'LEASE', 'TOSS_UP']).toContain(result.recommendation);
    expect(result.rationale.length).toBeGreaterThan(20);
  });

  it('computes a differential IRR', () => {
    expect(Number.isFinite(result.differentialIrr)).toBe(true);
  });
});

describe('breakEvenYear', () => {
  it('finds the first year cumulative differential turns positive', () => {
    // t0 -100, then +60, +60 => cumulative crosses 0 at year 2
    expect(breakEvenYear([-100, 60, 60, 60])).toBe(2);
  });

  it('returns null when it never crosses', () => {
    expect(breakEvenYear([-100, 10, 10])).toBeNull();
  });
});

describe('differentialCashFlow', () => {
  it('starts negative (buying ties up more cash) and lands net sale at year N', () => {
    const result = compare(MOCK_SUBJECT, market, DEFAULT_ASSUMPTIONS);
    const diff = differentialCashFlow(result.buy, result.lease);
    expect(diff[0]).toBeLessThan(0);
    expect(diff).toHaveLength(DEFAULT_ASSUMPTIONS.holdingPeriodYears + 1);
  });
});

describe('recommend', () => {
  it('recommends BUY when buying is cheaper and IRR beats the hurdle', () => {
    const { recommendation } = recommend(800_000, 1_000_000, 0.12, 0.08, 7, 10);
    expect(recommendation).toBe('BUY');
  });

  it('recommends LEASE when leasing is materially cheaper', () => {
    const { recommendation } = recommend(1_200_000, 1_000_000, 0.02, 0.08, null, 10);
    expect(recommendation).toBe('LEASE');
  });

  it('is a toss-up when costs are within tolerance', () => {
    const { recommendation } = recommend(1_000_000, 1_005_000, 0.03, 0.08, 9, 10);
    expect(recommendation).toBe('TOSS_UP');
  });
});

describe('runAnalysis — appreciation drives buy advantage over the hold', () => {
  it('long-term buy advantage improves with higher rent (value) growth', () => {
    const low = runAnalysis({
      subject: MOCK_SUBJECT,
      saleComps: MOCK_SALE_COMPS,
      leaseComps: MOCK_LEASE_COMPS,
      assumptions: { rentGrowthRate: 0.0 },
      skipSensitivity: true,
    });
    const high = runAnalysis({
      subject: MOCK_SUBJECT,
      saleComps: MOCK_SALE_COMPS,
      leaseComps: MOCK_LEASE_COMPS,
      assumptions: { rentGrowthRate: 0.04 },
      skipSensitivity: true,
    });
    expect(high.comparison.npvAdvantageOfBuying).toBeGreaterThan(
      low.comparison.npvAdvantageOfBuying
    );
  });

  it('builds a sensitivity grid by default', () => {
    const full = runAnalysis({
      subject: MOCK_SUBJECT,
      saleComps: MOCK_SALE_COMPS,
      leaseComps: MOCK_LEASE_COMPS,
    });
    expect(full.sensitivity.length).toBeGreaterThan(0);
    expect(full.sensitivity[0].cells.length).toBeGreaterThan(0);
  });
});
