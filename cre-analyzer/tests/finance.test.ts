import {
  amortizationSchedule,
  annualMortgagePayment,
  futureValue,
  grow,
  irr,
  mean,
  npv,
} from '../src/engine/finance';

describe('annualMortgagePayment', () => {
  it('matches the standard amortization formula', () => {
    // $1,000,000 @ 6.5% over 25 yrs (annual) ~ $81,981/yr
    const pmt = annualMortgagePayment(1_000_000, 0.065, 25);
    expect(pmt).toBeGreaterThan(81000);
    expect(pmt).toBeLessThan(83000);
  });

  it('handles a zero rate as simple division', () => {
    expect(annualMortgagePayment(100000, 0, 10)).toBe(10000);
  });

  it('is zero for no principal', () => {
    expect(annualMortgagePayment(0, 0.05, 20)).toBe(0);
  });
});

describe('amortizationSchedule', () => {
  it('pays the loan down over time', () => {
    const sched = amortizationSchedule(1_000_000, 0.065, 25, 10);
    expect(sched).toHaveLength(10);
    expect(sched[9].balanceEnd).toBeLessThan(1_000_000);
    expect(sched[0].interest).toBeGreaterThan(sched[9].interest);
    expect(sched[0].principal).toBeLessThan(sched[9].principal);
  });
});

describe('npv', () => {
  it('discounts a simple stream correctly', () => {
    // -100 now, +110 in one year @ 10% => 0
    expect(npv(0.1, [-100, 110])).toBeCloseTo(0, 6);
  });
});

describe('irr', () => {
  it('finds the rate that zeroes NPV', () => {
    expect(irr([-100, 110])).toBeCloseTo(0.1, 4);
  });

  it('solves a multi-period vector', () => {
    const r = irr([-1000, 300, 300, 300, 300]);
    expect(r).toBeGreaterThan(0.07);
    expect(r).toBeLessThan(0.08);
  });

  it('returns NaN when there is no sign change', () => {
    expect(Number.isNaN(irr([100, 200, 300]))).toBe(true);
  });
});

describe('helpers', () => {
  it('futureValue compounds', () => {
    expect(futureValue(100, 0.1, 2)).toBeCloseTo(121, 6);
  });
  it('grow compounds a per-period base', () => {
    expect(grow(10, 0.03, 1)).toBeCloseTo(10.3, 6);
  });
  it('mean averages', () => {
    expect(mean([2, 4, 6])).toBe(4);
    expect(mean([])).toBe(0);
  });
});
