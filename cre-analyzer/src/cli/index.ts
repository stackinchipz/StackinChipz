#!/usr/bin/env node
/**
 * cre-analyzer CLI.
 *
 *   cre-analyzer analyze --provider mock --address "123 Industrial Way, Austin, TX"
 */
import { Command } from 'commander';
import { AnalysisAssumptions } from '../types';
import { runAnalysis } from '../engine/analysis';
import { createProvider } from '../providers';
import { ConsoleReporter } from '../reporters/ConsoleReporter';
import { JsonReporter } from '../reporters/JsonReporter';
import { HtmlReporter } from '../reporters/HtmlReporter';
import { registerCalcCommands } from './calc';
import { registerRobotaxiCommand } from './robotaxi';

const program = new Command();

program
  .name('cre-analyzer')
  .description('Commercial Real Estate Lease vs. Buy analysis with property-tax normalization')
  .version('1.0.0');

registerCalcCommands(program);
registerRobotaxiCommand(program);

program
  .command('analyze')
  .description('Run a Lease vs. Buy analysis for a subject property')
  .requiredOption('--address <address>', 'Subject property address')
  .option('--provider <name>', 'Data provider: mock | manual | costar | crexi | loopnet', 'mock')
  .option('--holding-period <years>', 'Holding period (years)', parseFloat)
  .option('--discount-rate <rate>', 'Discount rate / WACC (decimal)', parseFloat)
  .option('--ltv <ratio>', 'Loan-to-value (decimal)', parseFloat)
  .option('--interest-rate <rate>', 'Mortgage interest rate (decimal)', parseFloat)
  .option('--amort-years <years>', 'Amortization period (years)', parseFloat)
  .option('--exit-cap-premium <bps>', 'Exit cap premium over entry (decimal, e.g. 0.0075)', parseFloat)
  .option('--rent-growth <rate>', 'Annual market-rent growth (decimal)', parseFloat)
  .option('--tax-growth <rate>', 'Annual property-tax growth (decimal)', parseFloat)
  .option('--output <format>', 'Console output: table | json', 'table')
  .option('--json [path]', 'Also export JSON (optional path)')
  .option('--report [path]', 'Generate an HTML report (optional path)')
  .option('--no-sensitivity', 'Skip the sensitivity grid (faster)')
  .action(async (opts) => {
    try {
      await runAnalyzeCommand(opts);
    } catch (err) {
      console.error(`\nError: ${(err as Error).message}\n`);
      process.exitCode = 1;
    }
  });

interface AnalyzeOpts {
  address: string;
  provider: string;
  holdingPeriod?: number;
  discountRate?: number;
  ltv?: number;
  interestRate?: number;
  amortYears?: number;
  exitCapPremium?: number;
  rentGrowth?: number;
  taxGrowth?: number;
  output: string;
  json?: string | boolean;
  report?: string | boolean;
  sensitivity: boolean;
}

async function runAnalyzeCommand(opts: AnalyzeOpts): Promise<void> {
  const provider = createProvider(opts.provider);
  if (provider.requiresCredentials) {
    console.log(
      `Provider "${provider.name}" requires credentials. ` +
        `See README for setup; falling through to its loader...`
    );
  }

  const bundle = await provider.fetchBundle({ address: opts.address });

  const overrides: Partial<AnalysisAssumptions> = {};
  if (opts.holdingPeriod != null) overrides.holdingPeriodYears = opts.holdingPeriod;
  if (opts.discountRate != null) overrides.discountRate = opts.discountRate;
  if (opts.ltv != null) overrides.ltv = opts.ltv;
  if (opts.interestRate != null) overrides.interestRate = opts.interestRate;
  if (opts.amortYears != null) overrides.amortizationYears = opts.amortYears;
  if (opts.exitCapPremium != null) overrides.exitCapPremium = opts.exitCapPremium;
  if (opts.rentGrowth != null) overrides.rentGrowthRate = opts.rentGrowth;
  if (opts.taxGrowth != null) overrides.taxGrowthRate = opts.taxGrowth;

  const result = runAnalysis({
    subject: bundle.subject,
    saleComps: bundle.saleComps,
    leaseComps: bundle.leaseComps,
    assumptions: overrides,
    skipSensitivity: opts.sensitivity === false,
  });

  if (opts.output === 'json') {
    console.log(new JsonReporter().serialize(result));
  } else {
    new ConsoleReporter().render(result);
  }

  if (opts.json) {
    const path = typeof opts.json === 'string' ? opts.json : './cre-analysis.json';
    new JsonReporter().write(result, path);
    console.log(`JSON written to ${path}`);
  }

  if (opts.report) {
    const path =
      typeof opts.report === 'string' ? opts.report : './cre-analysis-report.html';
    new HtmlReporter().write(result, path);
    console.log(`HTML report written to ${path}`);
  }
}

// Default to interactive help when no subcommand is given.
if (process.argv.length <= 2) {
  program.outputHelp();
} else {
  program.parse(process.argv);
}

export { program };
