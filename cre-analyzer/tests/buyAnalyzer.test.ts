import { analyzeBuy, noiForYear, projectedPropertyTax } from '../src/engine/buyAnalyzer';
import { deriveMarket } from '../src/engine/compSelector';
import { DEFAULT_ASSUMPTIONS } from '../src/engine/analysis';
import {
  MOCK_LEASE_COMPS,
  MOCK_SALE_COMPS,
  MOCK_SUBJECT,
} from '../src/providers/MockProvider';

const market = deriveMarket(MOCK_SUBJECT, MOCK_SALE_COMPS, MOCK_LEASE_COMPS);

describe('projectedPropertyTax', () => {
  it('uses the post-reassessment bill in year 1', () => {
    const t = projectedPropertyTax(MOCK_SUBJECT, DEFAULT_ASSUMPTIONS, 1);
    expect(t).toBeCloseTo(MOCK_SUBJECT.taxContext.estimatedPostTransactionTax, 2);
  });

  it('grows the bill subject to the statutory cap in later years', () => {
    const y1 = projectedPropertyTax(MOCK_SUBJECT, DEFAULT_ASSUMPTIONS, 1);
    const y5 = projectedPropertyTax(MOCK_SUBJECT, DEFAULT_ASSUMPTIONS, 5);
    expect(y5).toBeGreaterThan(y1);
  });
});

describe('noiForYear', () => {
  it('produces a tax-inclusive NOI', () => {
    const { noi, grossRent, propertyTax } = noiForYear(
      MOCK_SUBJECT,
      market,
      DEFAULT_ASSUMPTIONS,
      1
    );
    expect(grossRent).toBeGreaterThan(0);
    expect(propertyTax).toBeGreaterThan(0);
    expect(noi).toBeLessThan(grossRent); // expenses + tax reduce NOI
  });
});

describe('analyzeBuy — mock industrial', () => {
  const buy = analyzeBuy(MOCK_SUBJECT, market, DEFAULT_ASSUMPTIONS);

  it('derives a sensible purchase price from sale comps', () => {
    // ~ $180/SF avg * 20,000 SF
    expect(buy.purchasePrice).toBeGreaterThan(3_000_000);
    expect(buy.purchasePrice).toBeLessThan(4_500_000);
  });

  it('finances at the configured LTV', () => {
    expect(buy.loanAmount).toBeCloseTo(buy.purchasePrice * 0.7, 0);
    expect(buy.equity).toBeCloseTo(buy.purchasePrice * 0.3, 0);
  });

  it('builds a full 10-year cash flow', () => {
    expect(buy.cashFlows).toHaveLength(10);
    expect(buy.investmentCashFlowVector).toHaveLength(11);
    expect(buy.investmentCashFlowVector[0]).toBeLessThan(0); // equity outflow
  });

  it('produces a finite levered IRR in a believable band', () => {
    expect(Number.isFinite(buy.irr)).toBe(true);
    expect(buy.irr).toBeGreaterThan(0);
    expect(buy.irr).toBeLessThan(0.3);
  });

  it('sets the exit cap above the entry cap', () => {
    expect(buy.exitCapRate).toBeGreaterThan(buy.entryCapRate);
    expect(buy.terminalValue).toBeGreaterThan(0);
  });

  it('pays the loan down to a positive remaining balance', () => {
    const lastBal = buy.cashFlows[9].loanBalanceEnd;
    expect(lastBal).toBeGreaterThan(0);
    expect(lastBal).toBeLessThan(buy.loanAmount);
  });
});
