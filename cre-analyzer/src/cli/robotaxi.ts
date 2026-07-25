/**
 * `cre-analyzer robotaxi ...` — Lease vs. Buy for a robotaxi charging depot,
 * modeling landlord recapture of tenant-installed power at renewal.
 *
 * Examples:
 *   cre-analyzer robotaxi
 *   cre-analyzer robotaxi --scenario pivot
 *   cre-analyzer robotaxi --mw 8 --capex-per-mw 1500000 --capture 0.8 --fixed-renewal
 *   cre-analyzer robotaxi --json ./rt.json
 */
import { Command } from 'commander';
import {
  analyzeRobotaxi,
  DEFAULT_ROBOTAXI,
  RECAPTURE_PIVOT_SCENARIO,
  robotaxiSensitivity,
  RobotaxiParams,
} from '../engine/robotaxi';
import { writeFileSync } from 'fs';

const usd = (n: number): string => `$${Math.round(n).toLocaleString('en-US')}`;
const usdSf = (n: number): string => `$${n.toFixed(2)}/SF`;
const pct = (n: number): string => `${(n * 100).toFixed(1)}%`;

function optNum(value: string | undefined): number | undefined {
  if (value == null) return undefined;
  const n = Number(value);
  if (!Number.isFinite(n)) throw new Error(`Expected a number, got "${value}".`);
  return n;
}

export function registerRobotaxiCommand(program: Command): void {
  program
    .command('robotaxi')
    .description('Lease vs. Buy for a robotaxi charging pad with landlord power-recapture')
    .option('--scenario <name>', 'Base scenario: default | pivot', 'default')
    .option('--pad-sqft <n>', 'Pad rentable SF')
    .option('--base-rent <n>', 'Pre-power base industrial rent ($/SF/yr)')
    .option('--entry-cap <n>', 'Entry cap rate (decimal)')
    .option('--exit-cap-premium <n>', 'Exit cap premium over entry (decimal)')
    .option('--mw <n>', 'Power capacity (MW)')
    .option('--capex-per-mw <n>', 'Installed power cost ($/MW)')
    .option('--uplift-per-sf-per-mw <n>', 'HBU rent uplift ($/SF/yr per MW)')
    .option('--capture <n>', 'Landlord recapture fraction at renewal [0..1]')
    .option('--renewal-cap <n>', 'Cap on renewal rent jump (decimal)')
    .option('--fixed-renewal', 'Tenant holds a fixed-rate renewal option (blocks recapture)')
    .option('--initial-term <n>', 'Initial lease term (years)')
    .option('--renewal-term <n>', 'Renewal term length (years)')
    .option('--hold <n>', 'Holding period (years)')
    .option('--discount-rate <n>', 'Discount rate / WACC (decimal)')
    .option('--ltv <n>', 'Loan-to-value (decimal)')
    .option('--interest-rate <n>', 'Mortgage rate (decimal)')
    .option('--rent-growth <n>', 'Annual base rent growth (decimal)')
    .option('--json [path]', 'Export JSON (optional path)')
    .action((opts) => {
      try {
        runRobotaxi(opts);
      } catch (err) {
        console.error(`\nError: ${(err as Error).message}\n`);
        process.exitCode = 1;
      }
    });
}

interface RobotaxiOpts {
  scenario: string;
  padSqft?: string;
  baseRent?: string;
  entryCap?: string;
  exitCapPremium?: string;
  mw?: string;
  capexPerMw?: string;
  upliftPerSfPerMw?: string;
  capture?: string;
  renewalCap?: string;
  fixedRenewal?: boolean;
  initialTerm?: string;
  renewalTerm?: string;
  hold?: string;
  discountRate?: string;
  ltv?: string;
  interestRate?: string;
  rentGrowth?: string;
  json?: string | boolean;
}

function runRobotaxi(opts: RobotaxiOpts): void {
  const base =
    opts.scenario === 'pivot' ? RECAPTURE_PIVOT_SCENARIO : DEFAULT_ROBOTAXI;

  const p: RobotaxiParams = {
    ...base,
    ...defined({
      padSqFt: optNum(opts.padSqft),
      baseIndustrialRentPerSqFtYr: optNum(opts.baseRent),
      entryCapRate: optNum(opts.entryCap),
      exitCapPremium: optNum(opts.exitCapPremium),
      powerCapacityMW: optNum(opts.mw),
      powerCapexPerMW: optNum(opts.capexPerMw),
      hbuRentUpliftPerSqFtPerMW: optNum(opts.upliftPerSfPerMw),
      landlordCaptureFraction: optNum(opts.capture),
      renewalEscalationCapPct: optNum(opts.renewalCap),
      initialLeaseTermYears: optNum(opts.initialTerm),
      renewalTermYears: optNum(opts.renewalTerm),
      holdingPeriodYears: optNum(opts.hold),
      discountRate: optNum(opts.discountRate),
      ltv: optNum(opts.ltv),
      interestRate: optNum(opts.interestRate),
      rentGrowthRate: optNum(opts.rentGrowth),
    }),
  };
  if (opts.fixedRenewal) p.hasFixedRateRenewalOption = true;

  const r = analyzeRobotaxi(p);

  console.log('\n=== ROBOTAXI CHARGING — LEASE vs BUY ===');
  console.log(
    `${p.padSqFt.toLocaleString()} SF pad · ${p.powerCapacityMW} MW power · ` +
      `${p.holdingPeriodYears}-yr hold · ${p.initialLeaseTermYears}+${p.renewalTermYears} lease`
  );
  console.table([
    { Metric: 'Base pad price', Value: usd(r.purchasePrice) },
    { Metric: 'Power capex', Value: usd(r.powerCapex) },
    { Metric: 'Equity + closing (buy)', Value: usd(r.equity + r.closingCosts) },
    { Metric: 'Annual debt service', Value: usd(r.annualDebtService) },
    { Metric: 'Terminal value (exit)', Value: usd(r.terminalValue) },
    { Metric: 'Net sale proceeds', Value: usd(r.netSaleProceeds) },
  ]);

  console.log('\n--- Lease rent trajectory ($/SF) — watch the renewal re-rate ---');
  console.table(
    r.leaseRentPerSqFt.map((rent, i) => ({ Year: i + 1, 'Rent/SF': usdSf(rent) }))
  );

  console.log('\n--- Decision ---');
  console.table([
    { Metric: 'Buy NPV cost', Value: usd(r.buyNpvCost) },
    { Metric: 'Lease NPV cost', Value: usd(r.leaseNpvCost) },
    { Metric: 'NPV advantage of buying', Value: usd(r.npvAdvantageOfBuying) },
    { Metric: 'Landlord capture (input)', Value: pct(p.landlordCaptureFraction) },
    {
      Metric: 'Break-even capture',
      Value:
        r.breakEvenLandlordCapture == null
          ? 'lease wins at any capture'
          : r.breakEvenLandlordCapture === 0
          ? 'buy wins at 0% capture'
          : pct(r.breakEvenLandlordCapture),
    },
    { Metric: 'RECOMMENDATION', Value: r.recommendation },
  ]);
  console.log(`\n${r.rationale}\n`);

  // Sensitivity: capture x exit cap.
  const captures = [0, 0.25, 0.5, 0.75, 1];
  const exitCaps = [p.entryCapRate + 0.0, p.entryCapRate + 0.005, p.entryCapRate + 0.01, p.entryCapRate + 0.02];
  const cells = robotaxiSensitivity(p, captures, exitCaps);
  console.log('--- Sensitivity: NPV advantage of buying (rows=capture, cols=exit cap) ---');
  const grid: Record<string, Record<string, string>> = {};
  for (const c of cells) {
    const rk = pct(c.landlordCaptureFraction);
    const ck = pct(c.exitCapRate);
    grid[rk] = grid[rk] ?? {};
    grid[rk][ck] = usd(c.npvAdvantageOfBuying);
  }
  console.table(grid);

  if (opts.json) {
    const path = typeof opts.json === 'string' ? opts.json : './robotaxi-analysis.json';
    writeFileSync(path, JSON.stringify({ params: p, result: r, sensitivity: cells }, null, 2));
    console.log(`JSON written to ${path}`);
  }
}

/** Drop undefined values so overrides don't clobber the base scenario. */
function defined<T extends object>(obj: T): Partial<T> {
  const out: Partial<T> = {};
  for (const [k, v] of Object.entries(obj)) {
    if (v !== undefined) (out as Record<string, unknown>)[k] = v;
  }
  return out;
}
