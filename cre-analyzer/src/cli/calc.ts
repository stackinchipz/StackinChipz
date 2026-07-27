/**
 * `cre-analyzer calc ...` — a CRE / financial calculator built on the same
 * money-safe engine as the full analysis.
 *
 * Examples:
 *   cre-analyzer calc mortgage --principal 2000000 --rate 0.065 --amort 25
 *   cre-analyzer calc caprate --noi 200000 --price 3000000
 *   cre-analyzer calc value --noi 200000 --caprate 0.07
 *   cre-analyzer calc noi --gpi 300000 --vacancy 0.05 --opex 90000
 *   cre-analyzer calc coc --cashflow 45000 --equity 600000
 *   cre-analyzer calc dscr --noi 200000 --debt 150000
 *   cre-analyzer calc npv --rate 0.08 --flows "-500000,60000,60000,660000"
 *   cre-analyzer calc irr --flows "-500000,60000,60000,660000"
 */
import { Command } from 'commander';
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
  npv,
  valueFromCap,
} from '../engine/calculators';

const usd = (n: number): string => `$${Math.round(n).toLocaleString('en-US')}`;
const usd2 = (n: number): string =>
  `$${n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const pct = (n: number): string => `${(n * 100).toFixed(2)}%`;

/** Parse a required numeric flag, erroring clearly on bad input. */
function num(value: string | undefined, name: string): number {
  if (value == null) throw new Error(`Missing required option --${name}.`);
  const n = Number(value);
  if (!Number.isFinite(n)) throw new Error(`--${name} must be a number (got "${value}").`);
  return n;
}

/** Parse a comma/space separated list of numbers (for cash-flow vectors). */
function numList(value: string | undefined, name: string): number[] {
  if (value == null) throw new Error(`Missing required option --${name}.`);
  const parts = value
    .split(/[,\s]+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
  const nums = parts.map((p) => {
    const n = Number(p);
    if (!Number.isFinite(n)) throw new Error(`--${name} has a non-number: "${p}".`);
    return n;
  });
  if (nums.length === 0) throw new Error(`--${name} is empty.`);
  return nums;
}

function guard(fn: () => void): void {
  try {
    fn();
  } catch (err) {
    console.error(`Error: ${(err as Error).message}`);
    process.exitCode = 1;
  }
}

export function registerCalcCommands(program: Command): void {
  const calc = new Command('calc').description('CRE / financial calculators');

  calc
    .command('mortgage')
    .description('Loan payment, total interest, and amortization schedule')
    .requiredOption('--principal <amount>', 'Loan amount')
    .requiredOption('--rate <decimal>', 'Annual interest rate, e.g. 0.065')
    .requiredOption('--amort <years>', 'Amortization period in years')
    .option('--term <years>', 'Years to summarize (defaults to full amortization)')
    .option('--schedule', 'Print the annual amortization schedule')
    .action((o) =>
      guard(() => {
        const r = mortgage({
          principal: num(o.principal, 'principal'),
          annualRate: num(o.rate, 'rate'),
          amortYears: num(o.amort, 'amort'),
          termYears: o.term != null ? num(o.term, 'term') : undefined,
        });
        console.log(`\nMortgage — ${usd(r.principal)} @ ${pct(r.annualRate)} / ${r.amortYears}yr`);
        console.log(`  Annual payment : ${usd2(r.annualPayment)}`);
        console.log(`  Monthly payment: ${usd2(r.monthlyPayment)}`);
        console.log(`  Over ${r.termYears} yr: paid ${usd(r.totalPaidOverTerm)}, ` +
          `interest ${usd(r.totalInterestOverTerm)}`);
        console.log(`  Balance at term end: ${usd(r.balanceAtTermEnd)}`);
        if (o.schedule) {
          console.log('');
          console.table(
            r.schedule.map((s) => ({
              Yr: s.year,
              Interest: usd(s.interest),
              Principal: usd(s.principal),
              'Balance End': usd(s.balanceEnd),
            }))
          );
        }
        console.log('');
      })
    );

  calc
    .command('caprate')
    .description('Cap rate = NOI / value')
    .requiredOption('--noi <amount>', 'Net operating income')
    .requiredOption('--price <amount>', 'Value / purchase price')
    .action((o) =>
      guard(() => {
        const rate = capRate(num(o.noi, 'noi'), num(o.price, 'price'));
        console.log(`\nCap rate: ${pct(rate)}  (NOI ${usd(num(o.noi, 'noi'))} / ${usd(num(o.price, 'price'))})\n`);
      })
    );

  calc
    .command('value')
    .description('Value = NOI / cap rate')
    .requiredOption('--noi <amount>', 'Net operating income')
    .requiredOption('--caprate <decimal>', 'Cap rate, e.g. 0.07')
    .action((o) =>
      guard(() => {
        const value = valueFromCap(num(o.noi, 'noi'), num(o.caprate, 'caprate'));
        console.log(`\nValue: ${usd(value)}  (NOI ${usd(num(o.noi, 'noi'))} @ ${pct(num(o.caprate, 'caprate'))})\n`);
      })
    );

  calc
    .command('noi')
    .description('NOI from gross income, vacancy, and OpEx')
    .requiredOption('--gpi <amount>', 'Gross potential income')
    .option('--vacancy <decimal>', 'Vacancy rate, e.g. 0.05', '0')
    .option('--other <amount>', 'Other income', '0')
    .requiredOption('--opex <amount>', 'Operating expenses')
    .action((o) =>
      guard(() => {
        const r = computeNoi({
          grossPotentialIncome: num(o.gpi, 'gpi'),
          vacancyRate: num(o.vacancy, 'vacancy'),
          otherIncome: num(o.other, 'other'),
          operatingExpenses: num(o.opex, 'opex'),
        });
        console.log('');
        console.log(`  Gross potential income : ${usd(r.grossPotentialIncome)}`);
        console.log(`  Vacancy loss           : -${usd(r.vacancyLoss)}`);
        console.log(`  Effective gross income : ${usd(r.effectiveGrossIncome)}`);
        console.log(`  Operating expenses     : -${usd(r.operatingExpenses)}`);
        console.log(`  NOI                    : ${usd(r.noi)}\n`);
      })
    );

  calc
    .command('coc')
    .description('Cash-on-cash return = annual cash flow / equity')
    .requiredOption('--cashflow <amount>', 'Annual pre-tax cash flow')
    .requiredOption('--equity <amount>', 'Equity invested')
    .action((o) =>
      guard(() => {
        const r = cashOnCash(num(o.cashflow, 'cashflow'), num(o.equity, 'equity'));
        console.log(`\nCash-on-cash: ${pct(r)}\n`);
      })
    );

  calc
    .command('dscr')
    .description('Debt-service coverage ratio = NOI / debt service')
    .requiredOption('--noi <amount>', 'Net operating income')
    .requiredOption('--debt <amount>', 'Annual debt service')
    .action((o) =>
      guard(() => {
        const r = dscr(num(o.noi, 'noi'), num(o.debt, 'debt'));
        const verdict = r >= 1.25 ? 'healthy (>=1.25)' : r >= 1.0 ? 'thin' : 'below breakeven';
        console.log(`\nDSCR: ${r.toFixed(2)}x  (${verdict})\n`);
      })
    );

  calc
    .command('grm')
    .description('Gross rent multiplier = price / gross income')
    .requiredOption('--price <amount>', 'Price')
    .requiredOption('--gross <amount>', 'Gross annual income')
    .action((o) =>
      guard(() => {
        const r = grossRentMultiplier(num(o.price, 'price'), num(o.gross, 'gross'));
        console.log(`\nGross rent multiplier: ${r.toFixed(2)}x\n`);
      })
    );

  calc
    .command('breakeven')
    .description('Break-even occupancy = (OpEx + debt service) / gross income')
    .requiredOption('--opex <amount>', 'Operating expenses')
    .requiredOption('--debt <amount>', 'Annual debt service')
    .requiredOption('--gpi <amount>', 'Gross potential income')
    .action((o) =>
      guard(() => {
        const r = breakEvenOccupancy(
          num(o.opex, 'opex'),
          num(o.debt, 'debt'),
          num(o.gpi, 'gpi')
        );
        console.log(`\nBreak-even occupancy: ${pct(r)}\n`);
      })
    );

  calc
    .command('maxloan')
    .description('Max supportable loan from NOI + required DSCR')
    .requiredOption('--noi <amount>', 'Net operating income')
    .requiredOption('--dscr <ratio>', 'Required DSCR, e.g. 1.25')
    .requiredOption('--rate <decimal>', 'Annual interest rate, e.g. 0.065')
    .requiredOption('--amort <years>', 'Amortization period in years')
    .action((o) =>
      guard(() => {
        const r = maxLoanFromDscr(
          num(o.noi, 'noi'),
          num(o.dscr, 'dscr'),
          num(o.rate, 'rate'),
          num(o.amort, 'amort')
        );
        console.log(`\nMax supportable loan: ${usd(r)}  (DSCR ${num(o.dscr, 'dscr')}x @ ${pct(num(o.rate, 'rate'))})\n`);
      })
    );

  calc
    .command('npv')
    .description('Net present value of a cash-flow vector (index 0 = time 0)')
    .requiredOption('--rate <decimal>', 'Discount rate, e.g. 0.08')
    .requiredOption('--flows <list>', 'Comma-separated cash flows, e.g. "-500000,60000,660000"')
    .action((o) =>
      guard(() => {
        const flows = numList(o.flows, 'flows');
        const r = npv(num(o.rate, 'rate'), flows);
        console.log(`\nNPV @ ${pct(num(o.rate, 'rate'))}: ${usd2(r)}  (${flows.length} periods)\n`);
      })
    );

  calc
    .command('irr')
    .description('Internal rate of return of a cash-flow vector (index 0 = time 0)')
    .requiredOption('--flows <list>', 'Comma-separated cash flows, e.g. "-500000,60000,660000"')
    .action((o) =>
      guard(() => {
        const flows = numList(o.flows, 'flows');
        const r = irr(flows);
        console.log(
          Number.isNaN(r)
            ? '\nIRR: undefined (cash flows never change sign)\n'
            : `\nIRR: ${pct(r)}  (${flows.length} periods)\n`
        );
      })
    );

  program.addCommand(calc);
}
