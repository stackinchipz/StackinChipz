/**
 * Robotaxi charging depot — Lease vs. Buy with landlord power-recapture.
 *
 * THE THESIS: a robotaxi charging tenant sinks large, IMMOVABLE capital into the
 * pad — bringing in megawatts of utility power (service upgrade, transformers,
 * switchgear, sometimes an on-site substation). That capex permanently raises
 * the pad's highest-and-best-use (HBU) rent. At renewal the landlord re-rates to
 * that new HBU and captures value the TENANT paid to create (the appropriable-
 * quasi-rent / "holdup" problem). Buying eliminates that recapture and lets the
 * occupier keep the power-driven value as appreciation at exit.
 *
 * This module quantifies how much the recapture lowers the buy-vs-lease
 * threshold. All functions are PURE.
 */
import { amortizationSchedule, annualMortgagePayment, grow, money, npv, round } from './finance';

export interface RobotaxiParams {
  // --- Pad + base market ---
  padSqFt: number;
  baseIndustrialRentPerSqFtYr: number; // pre-power market rent ($/SF/yr)
  entryCapRate: number; // used to value the base industrial pad
  exitCapPremium: number; // bps over entry cap at exit

  // --- Power upgrade (the specific investment) ---
  powerCapacityMW: number;
  powerCapexPerMW: number; // $/MW installed
  hbuRentUpliftPerSqFtPerMW: number; // $/SF/yr of HBU rent uplift per MW
  removableEquipmentFraction: number; // [0,1] portion of power capex that is recoverable trade fixtures
  equipmentResidualPct: number; // [0,1] salvage value of that removable portion at lease end

  // --- Lease renewal structure (the recapture knobs) ---
  landlordCaptureFraction: number; // [0,1] share of HBU uplift re-rated into renewal rent
  initialLeaseTermYears: number;
  renewalTermYears: number;
  renewalEscalationCapPct: number; // cap on the renewal rent jump vs prior year
  hasFixedRateRenewalOption: boolean; // contractual renewal (no HBU capture) if true
  leaseUpfrontPerSqFt: number; // legal/broker/moving at signing

  // --- Finance ---
  holdingPeriodYears: number;
  discountRate: number;
  ltv: number;
  interestRate: number;
  amortizationYears: number;
  closingCostPct: number;
  sellingCostPct: number;
  rentGrowthRate: number; // base market escalation
}

export interface RobotaxiResult {
  purchasePrice: number;
  powerCapex: number;
  equity: number;
  loanAmount: number;
  closingCosts: number;
  annualDebtService: number;
  terminalValue: number;
  netSaleProceeds: number;
  buyCostVector: number[];
  leaseCostVector: number[];
  leaseRentPerSqFt: number[];
  buyNpvCost: number;
  leaseNpvCost: number;
  npvAdvantageOfBuying: number; // leaseNpvCost - buyNpvCost; positive => buy wins
  recommendation: 'BUY' | 'LEASE' | 'TOSS_UP';
  breakEvenLandlordCapture: number | null; // capture fraction where advantage == 0
  rationale: string;
}

export function powerUpliftPerSqFtYr(p: RobotaxiParams): number {
  return p.hbuRentUpliftPerSqFtPerMW * p.powerCapacityMW;
}

export function powerCapexTotal(p: RobotaxiParams): number {
  return p.powerCapacityMW * p.powerCapexPerMW;
}

/** Base industrial value of the pad (pre-power), NOI capitalized at entry cap. */
export function basePurchasePrice(p: RobotaxiParams): number {
  return (p.baseIndustrialRentPerSqFtYr * p.padSqFt) / p.entryCapRate;
}

/** The years (1-based) at which a lease renewal re-rate happens inside the hold. */
export function renewalYears(p: RobotaxiParams): number[] {
  const years: number[] = [];
  let y = p.initialLeaseTermYears + 1;
  while (y <= p.holdingPeriodYears) {
    years.push(y);
    y += p.renewalTermYears;
  }
  return years;
}

/**
 * Per-SF lease rent for each hold year. Rent starts at the pre-power base
 * (the tenant brought the power, so the initial rent doesn't price it in),
 * escalates contractually within a term, and re-rates at each renewal — that
 * re-rate is where the landlord captures the tenant's power uplift.
 */
export function leaseRentPerSqFtSchedule(p: RobotaxiParams): number[] {
  const N = p.holdingPeriodYears;
  const renewals = new Set(renewalYears(p));
  const schedule: number[] = [];
  let rent = p.baseIndustrialRentPerSqFtYr;

  for (let year = 1; year <= N; year++) {
    if (year === 1) {
      rent = p.baseIndustrialRentPerSqFtYr;
    } else if (renewals.has(year)) {
      const marketBase = grow(p.baseIndustrialRentPerSqFtYr, p.rentGrowthRate, year - 1);
      const uplift = grow(powerUpliftPerSqFtYr(p), p.rentGrowthRate, year - 1);
      if (p.hasFixedRateRenewalOption) {
        // Contractual renewal option: rent bumps at base escalation, no HBU capture.
        rent = rent * (1 + p.rentGrowthRate);
      } else {
        const target = marketBase + p.landlordCaptureFraction * uplift;
        const capped = rent * (1 + p.renewalEscalationCapPct);
        rent = Math.min(target, capped);
        rent = Math.max(rent, marketBase); // landlord won't re-rate below market
      }
    } else {
      rent = rent * (1 + p.rentGrowthRate);
    }
    schedule.push(round(rent, 4));
  }
  return schedule;
}

interface Npvs {
  buyNpvCost: number;
  leaseNpvCost: number;
  buyCostVector: number[];
  leaseCostVector: number[];
  leaseRentPerSqFt: number[];
  purchasePrice: number;
  powerCapex: number;
  equity: number;
  loanAmount: number;
  closingCosts: number;
  annualDebtService: number;
  terminalValue: number;
  netSaleProceeds: number;
}

/** Core NPV computation (no break-even solve — keeps break-even from recursing). */
export function computeNpvs(p: RobotaxiParams): Npvs {
  const N = p.holdingPeriodYears;
  const price = money(basePurchasePrice(p));
  const power = money(powerCapexTotal(p));
  const loan = money(price * p.ltv);
  const equity = money(price - loan);
  const closing = money(price * p.closingCostPct);
  const ds = annualMortgagePayment(loan, p.interestRate, p.amortizationYears);
  const sched = amortizationSchedule(loan, p.interestRate, p.amortizationYears, N);

  // ----- BUY cost vector (positive = cost; terminal is a large credit) -----
  const buyVec: number[] = [money(equity + closing + power)];
  let terminalValue = 0;
  let netSale = 0;
  for (let year = 1; year <= N; year++) {
    let cost = ds;
    if (year === N) {
      const baseNext = grow(p.baseIndustrialRentPerSqFtYr, p.rentGrowthRate, N);
      const upliftNext = grow(powerUpliftPerSqFtYr(p), p.rentGrowthRate, N);
      const terminalNoi = (baseNext + upliftNext) * p.padSqFt; // owner captures the FULL uplift
      const exitCap = p.entryCapRate + p.exitCapPremium;
      terminalValue = money(terminalNoi / exitCap);
      const sellingCosts = money(terminalValue * p.sellingCostPct);
      const payoff = sched[N - 1].balanceEnd;
      netSale = money(terminalValue - sellingCosts - payoff);
      cost = money(cost - netSale);
    }
    buyVec.push(money(cost));
  }
  const buyNpvCost = npv(p.discountRate, buyVec);

  // ----- LEASE cost vector -----
  const rentSched = leaseRentPerSqFtSchedule(p);
  const leaseVec: number[] = [money(power + p.leaseUpfrontPerSqFt * p.padSqFt)];
  for (let year = 1; year <= N; year++) {
    let cost = rentSched[year - 1] * p.padSqFt;
    if (year === N) {
      const salvage = p.removableEquipmentFraction * power * p.equipmentResidualPct;
      cost = cost - salvage; // tenant recovers only removable trade fixtures
    }
    leaseVec.push(money(cost));
  }
  const leaseNpvCost = npv(p.discountRate, leaseVec);

  return {
    buyNpvCost,
    leaseNpvCost,
    buyCostVector: buyVec,
    leaseCostVector: leaseVec,
    leaseRentPerSqFt: rentSched,
    purchasePrice: price,
    powerCapex: power,
    equity,
    loanAmount: loan,
    closingCosts: closing,
    annualDebtService: ds,
    terminalValue,
    netSaleProceeds: netSale,
  };
}

/**
 * The landlord capture fraction at which Buy NPV cost == Lease NPV cost.
 * Advantage-of-buying is monotonically increasing in capture, so we bisect.
 * Returns null when even full capture (1.0) doesn't make buying win, or when
 * buying already wins at zero capture (break-even below the [0,1] range).
 */
export function solveBreakEvenCapture(p: RobotaxiParams): number | null {
  const advantage = (c: number): number => {
    const r = computeNpvs({ ...p, landlordCaptureFraction: c });
    return r.leaseNpvCost - r.buyNpvCost;
  };
  const at0 = advantage(0);
  const at1 = advantage(1);
  if (at0 >= 0) return 0; // buying already wins with no recapture
  if (at1 < 0) return null; // leasing wins even at full recapture

  let lo = 0;
  let hi = 1;
  for (let i = 0; i < 100; i++) {
    const mid = (lo + hi) / 2;
    const f = advantage(mid);
    if (Math.abs(f) < 1) return round(mid, 6);
    if (f < 0) lo = mid;
    else hi = mid;
  }
  return round((lo + hi) / 2, 6);
}

export function analyzeRobotaxi(p: RobotaxiParams): RobotaxiResult {
  const n = computeNpvs(p);
  const npvAdvantageOfBuying = money(n.leaseNpvCost - n.buyNpvCost);
  const breakEven = solveBreakEvenCapture(p);

  const denom = Math.max(Math.abs(n.leaseNpvCost), 1);
  const advPct = npvAdvantageOfBuying / denom;
  let recommendation: 'BUY' | 'LEASE' | 'TOSS_UP';
  if (advPct > 0.02) recommendation = 'BUY';
  else if (advPct < -0.02) recommendation = 'LEASE';
  else recommendation = 'TOSS_UP';

  const beStr =
    breakEven == null
      ? 'leasing wins even at 100% landlord capture'
      : breakEven === 0
      ? 'buying wins even at 0% capture'
      : `buying wins once the landlord captures ≥ ${(breakEven * 100).toFixed(0)}% of your power uplift`;

  const rationale =
    `Buy NPV cost $${Math.round(n.buyNpvCost).toLocaleString()} vs Lease NPV cost ` +
    `$${Math.round(n.leaseNpvCost).toLocaleString()} ` +
    `(buying ${npvAdvantageOfBuying >= 0 ? 'saves' : 'costs'} ` +
    `$${Math.abs(Math.round(npvAdvantageOfBuying)).toLocaleString()} NPV). ` +
    `Power capex $${Math.round(n.powerCapex).toLocaleString()} for ${p.powerCapacityMW} MW. ` +
    `Break-even: ${beStr}.`;

  return {
    purchasePrice: n.purchasePrice,
    powerCapex: n.powerCapex,
    equity: n.equity,
    loanAmount: n.loanAmount,
    closingCosts: n.closingCosts,
    annualDebtService: n.annualDebtService,
    terminalValue: n.terminalValue,
    netSaleProceeds: n.netSaleProceeds,
    buyCostVector: n.buyCostVector,
    leaseCostVector: n.leaseCostVector,
    leaseRentPerSqFt: n.leaseRentPerSqFt,
    buyNpvCost: n.buyNpvCost,
    leaseNpvCost: n.leaseNpvCost,
    npvAdvantageOfBuying,
    recommendation,
    breakEvenLandlordCapture: breakEven,
    rationale,
  };
}

export interface RobotaxiSensitivityCell {
  landlordCaptureFraction: number;
  exitCapRate: number;
  npvAdvantageOfBuying: number;
}

/** Grid of NPV advantage across landlord capture x exit cap (appreciation proxy). */
export function robotaxiSensitivity(
  p: RobotaxiParams,
  captureFractions: number[],
  exitCapRates: number[]
): RobotaxiSensitivityCell[] {
  const cells: RobotaxiSensitivityCell[] = [];
  for (const c of captureFractions) {
    for (const ec of exitCapRates) {
      const premium = ec - p.entryCapRate;
      const r = computeNpvs({
        ...p,
        landlordCaptureFraction: c,
        exitCapPremium: premium,
      });
      cells.push({
        landlordCaptureFraction: c,
        exitCapRate: ec,
        npvAdvantageOfBuying: money(r.leaseNpvCost - r.buyNpvCost),
      });
    }
  }
  return cells;
}

/**
 * A realistic default scenario: 40k SF pad, 5 MW, 10-yr hold, 5+5 lease.
 * Here buying wins even before recapture — the dominant driver is that the
 * owner keeps the value the $6M power investment creates (capitalized at exit),
 * which leasing forfeits. Recapture only widens the gap.
 */
export const DEFAULT_ROBOTAXI: RobotaxiParams = {
  padSqFt: 40000,
  baseIndustrialRentPerSqFtYr: 10,
  entryCapRate: 0.07,
  exitCapPremium: 0.005,
  powerCapacityMW: 5,
  powerCapexPerMW: 1_200_000,
  hbuRentUpliftPerSqFtPerMW: 0.9,
  removableEquipmentFraction: 0.35,
  equipmentResidualPct: 0.3,
  landlordCaptureFraction: 0.6,
  initialLeaseTermYears: 5,
  renewalTermYears: 5,
  renewalEscalationCapPct: 0.15,
  hasFixedRateRenewalOption: false,
  leaseUpfrontPerSqFt: 1.5,
  holdingPeriodYears: 10,
  discountRate: 0.08,
  ltv: 0.65,
  interestRate: 0.07,
  amortizationYears: 25,
  closingCostPct: 0.025,
  sellingCostPct: 0.05,
  rentGrowthRate: 0.03,
};

/**
 * A "recapture-pivot" scenario where landlord recapture is THE deciding factor.
 * Appreciation is roughly neutral (high discount + exit-cap expansion + costs),
 * the renewal cap is weak (uncapped re-rate), and the 15-yr hold spans two
 * renewals — so the decision flips from LEASE to BUY only once the landlord
 * captures a large share of the tenant-installed power uplift (break-even ~75%).
 * Use this to see the holdup mechanism in isolation.
 */
export const RECAPTURE_PIVOT_SCENARIO: RobotaxiParams = {
  ...DEFAULT_ROBOTAXI,
  discountRate: 0.105,
  interestRate: 0.085,
  exitCapPremium: 0.03,
  ltv: 0.55,
  sellingCostPct: 0.06,
  rentGrowthRate: 0.02,
  renewalEscalationCapPct: 1.0, // effectively uncapped renewal (weak tenant protection)
  hbuRentUpliftPerSqFtPerMW: 0.9,
  holdingPeriodYears: 15,
};
