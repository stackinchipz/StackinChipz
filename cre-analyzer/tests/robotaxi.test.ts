import {
  analyzeRobotaxi,
  computeNpvs,
  DEFAULT_ROBOTAXI,
  leaseRentPerSqFtSchedule,
  powerCapexTotal,
  powerUpliftPerSqFtYr,
  RECAPTURE_PIVOT_SCENARIO,
  renewalYears,
  robotaxiSensitivity,
  RobotaxiParams,
  solveBreakEvenCapture,
} from '../src/engine/robotaxi';

const advantage = (p: RobotaxiParams): number => {
  const n = computeNpvs(p);
  return n.leaseNpvCost - n.buyNpvCost;
};

describe('power helpers', () => {
  it('computes total power capex and per-SF uplift', () => {
    expect(powerCapexTotal(DEFAULT_ROBOTAXI)).toBe(5 * 1_200_000);
    expect(powerUpliftPerSqFtYr(DEFAULT_ROBOTAXI)).toBeCloseTo(0.9 * 5, 6);
  });
});

describe('renewal schedule', () => {
  it('places renewals after the initial term, every renewal term', () => {
    // 5-yr initial + 5-yr renewals over a 10-yr hold => renewal at year 6.
    expect(renewalYears(DEFAULT_ROBOTAXI)).toEqual([6]);
  });

  it('re-rates upward at renewal when the landlord captures uplift', () => {
    const sched = leaseRentPerSqFtSchedule({ ...DEFAULT_ROBOTAXI, landlordCaptureFraction: 1 });
    // Year 6 (renewal) rent should jump above the pure-escalation year-5 rent.
    const escalatedOnly = leaseRentPerSqFtSchedule({
      ...DEFAULT_ROBOTAXI,
      landlordCaptureFraction: 0,
      hasFixedRateRenewalOption: true,
    });
    expect(sched[5]).toBeGreaterThan(escalatedOnly[5]);
  });

  it('a fixed-rate renewal option blocks the HBU capture', () => {
    const withOption = leaseRentPerSqFtSchedule({
      ...DEFAULT_ROBOTAXI,
      landlordCaptureFraction: 1,
      hasFixedRateRenewalOption: true,
    });
    const withoutOption = leaseRentPerSqFtSchedule({
      ...DEFAULT_ROBOTAXI,
      landlordCaptureFraction: 1,
      hasFixedRateRenewalOption: false,
    });
    expect(withOption[5]).toBeLessThan(withoutOption[5]);
  });
});

describe('monotonicity — the core thesis', () => {
  it('the NPV advantage of buying rises monotonically with landlord capture', () => {
    let prev = -Infinity;
    for (const c of [0, 0.2, 0.4, 0.6, 0.8, 1]) {
      const adv = advantage({ ...DEFAULT_ROBOTAXI, landlordCaptureFraction: c });
      expect(adv).toBeGreaterThanOrEqual(prev - 1); // non-decreasing (tolerance for rounding)
      prev = adv;
    }
  });

  it('more landlord capture strictly helps buying vs zero capture', () => {
    const low = advantage({ ...DEFAULT_ROBOTAXI, landlordCaptureFraction: 0 });
    const high = advantage({ ...DEFAULT_ROBOTAXI, landlordCaptureFraction: 1 });
    expect(high).toBeGreaterThan(low);
  });
});

describe('break-even landlord capture — default (buy-favored) scenario', () => {
  it('returns 0 when buying already wins without any recapture', () => {
    // In the realistic default, keeping the power value at exit already favors
    // buying, so the break-even sits at (or below) zero capture.
    expect(solveBreakEvenCapture(DEFAULT_ROBOTAXI)).toBe(0);
  });
});

describe('break-even landlord capture — recapture-pivot scenario', () => {
  const breakEven = solveBreakEvenCapture(RECAPTURE_PIVOT_SCENARIO);

  it('is an interior fraction (recapture is the deciding factor)', () => {
    expect(breakEven).not.toBeNull();
    expect(breakEven!).toBeGreaterThan(0);
    expect(breakEven!).toBeLessThan(1);
  });

  it('yields ~zero NPV advantage when fed back in (±$1k)', () => {
    const adv = advantage({ ...RECAPTURE_PIVOT_SCENARIO, landlordCaptureFraction: breakEven! });
    expect(Math.abs(adv)).toBeLessThan(1000);
  });

  it('below break-even leases, above break-even buys', () => {
    const below = analyzeRobotaxi({ ...RECAPTURE_PIVOT_SCENARIO, landlordCaptureFraction: Math.max(0, breakEven! - 0.2) });
    const above = analyzeRobotaxi({ ...RECAPTURE_PIVOT_SCENARIO, landlordCaptureFraction: Math.min(1, breakEven! + 0.2) });
    expect(below.npvAdvantageOfBuying).toBeLessThan(0);
    expect(above.npvAdvantageOfBuying).toBeGreaterThan(0);
  });
});

describe('analyzeRobotaxi output', () => {
  const r = analyzeRobotaxi(DEFAULT_ROBOTAXI);

  it('derives price and power capex', () => {
    expect(r.purchasePrice).toBeGreaterThan(0);
    expect(r.powerCapex).toBe(6_000_000);
  });

  it('produces a recommendation and a rationale that names the recapture', () => {
    expect(['BUY', 'LEASE', 'TOSS_UP']).toContain(r.recommendation);
    expect(r.rationale.toLowerCase()).toContain('break-even');
  });

  it('builds cost vectors of the right length', () => {
    expect(r.buyCostVector).toHaveLength(DEFAULT_ROBOTAXI.holdingPeriodYears + 1);
    expect(r.leaseCostVector).toHaveLength(DEFAULT_ROBOTAXI.holdingPeriodYears + 1);
    expect(r.buyCostVector[0]).toBeGreaterThan(0); // upfront equity+closing+power
  });
});

describe('sensitivity grid', () => {
  it('covers every capture x exit-cap combination', () => {
    const cells = robotaxiSensitivity(DEFAULT_ROBOTAXI, [0, 0.5, 1], [0.06, 0.07, 0.08]);
    expect(cells).toHaveLength(9);
    // Higher capture => more advantage at a fixed exit cap.
    const atEc = cells.filter((c) => Math.abs(c.exitCapRate - 0.07) < 1e-9);
    expect(atEc[2].npvAdvantageOfBuying).toBeGreaterThan(atEc[0].npvAdvantageOfBuying);
  });
});
