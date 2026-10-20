import {
  breakEvenOccupancy,
  capRate,
  cashOnCash,
  computeNoi,
  dscr,
  grossRentMultiplier,
  irr,
  maxLoanFromDscr,
  mortgage,
  noiFromCap,
  npv,
  valueFromCap,
} from '../src/engine/calculators';

describe('cap rate triangle', () => {
  it('cap rate = NOI / value', () => {
    expect(capRate(210000, 3000000)).toBeCloseTo(0.07, 6);
  });
  it('value = NOI / cap rate', () => {
    expect(valueFromCap(210000, 0.07)).toBeCloseTo(3000000, 0);
  });
  it('NOI = value * cap rate', () => {
    expect(noiFromCap(3000000, 0.07)).toBeCloseTo(210000, 0);
  });
  it('round-trips', () => {
    const v = valueFromCap(210000, 0.07);
    expect(capRate(210000, v)).toBeCloseTo(0.07, 6);
  });
  it('throws on non-positive value', () => {
    expect(() => capRate(1, 0)).toThrow();
    expect(() => valueFromCap(1, 0)).toThrow();
  });
});

describe('computeNoi', () => {
  it('applies vacancy and other income', () => {
    const r = computeNoi({
      grossPotentialIncome: 300000,
      vacancyRate: 0.05,
      otherIncome: 10000,
      operatingExpenses: 90000,
    });
    expect(r.vacancyLoss).toBeCloseTo(15000, 2);
    expect(r.effectiveGrossIncome).toBeCloseTo(295000, 2); // 300k - 15k + 10k
    expect(r.noi).toBeCloseTo(205000, 2); // 295k - 90k
  });

  it('defaults vacancy and other income to zero', () => {
    const r = computeNoi({ grossPotentialIncome: 100000, operatingExpenses: 40000 });
    expect(r.noi).toBe(60000);
  });
});

describe('returns & coverage', () => {
  it('cash-on-cash', () => {
    expect(cashOnCash(45000, 600000)).toBeCloseTo(0.075, 6);
  });
  it('dscr', () => {
    expect(dscr(200000, 150000)).toBeCloseTo(1.3333, 4);
  });
  it('gross rent multiplier', () => {
    expect(grossRentMultiplier(3000000, 300000)).toBeCloseTo(10, 4);
  });
  it('break-even occupancy', () => {
    expect(breakEvenOccupancy(90000, 150000, 300000)).toBeCloseTo(0.8, 6);
  });
  it('guards against divide-by-zero', () => {
    expect(() => cashOnCash(1, 0)).toThrow();
    expect(() => dscr(1, 0)).toThrow();
    expect(() => grossRentMultiplier(1, 0)).toThrow();
    expect(() => breakEvenOccupancy(1, 1, 0)).toThrow();
  });
});

describe('mortgage', () => {
  const r = mortgage({ principal: 2000000, annualRate: 0.065, amortYears: 25 });

  it('computes annual and monthly payments', () => {
    expect(r.annualPayment).toBeGreaterThan(160000);
    expect(r.annualPayment).toBeLessThan(166000);
    expect(r.monthlyPayment).toBeCloseTo(r.annualPayment / 12, 2);
  });

  it('amortizes to ~zero over the full term', () => {
    expect(r.schedule).toHaveLength(25);
    expect(r.balanceAtTermEnd).toBeLessThan(1); // fully paid
  });

  it('total interest is positive and total paid exceeds principal', () => {
    expect(r.totalInterestOverTerm).toBeGreaterThan(0);
    expect(r.totalPaidOverTerm).toBeGreaterThan(r.principal);
  });

  it('honors a shorter reporting term', () => {
    const short = mortgage({ principal: 2000000, annualRate: 0.065, amortYears: 25, termYears: 10 });
    expect(short.schedule).toHaveLength(10);
    expect(short.balanceAtTermEnd).toBeGreaterThan(0); // not yet paid off
  });
});

describe('maxLoanFromDscr', () => {
  it('backs out a loan the NOI can cover at the required DSCR', () => {
    const loan = maxLoanFromDscr(200000, 1.25, 0.065, 25);
    // payment capacity = 200000/1.25 = 160000; that amortizes to < the 2M principal
    expect(loan).toBeGreaterThan(1_800_000);
    expect(loan).toBeLessThan(2_100_000);
  });

  it('a lower required DSCR supports a larger loan', () => {
    const strict = maxLoanFromDscr(200000, 1.5, 0.065, 25);
    const loose = maxLoanFromDscr(200000, 1.1, 0.065, 25);
    expect(loose).toBeGreaterThan(strict);
  });

  it('throws on non-positive DSCR', () => {
    expect(() => maxLoanFromDscr(1, 0, 0.05, 25)).toThrow();
  });
});

describe('npv / irr wrappers', () => {
  it('npv discounts correctly', () => {
    expect(npv(0.1, [-100, 110])).toBeCloseTo(0, 6);
  });
  it('irr solves the rate', () => {
    expect(irr([-100, 110])).toBeCloseTo(0.1, 4);
  });
  it('irr is NaN with no sign change', () => {
    expect(Number.isNaN(irr([100, 200]))).toBe(true);
  });
});
