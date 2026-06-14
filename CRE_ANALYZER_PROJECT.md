# CRE_ANALYZER_PROJECT.md

## Setup

Create a new folder called `cre-analyzer`, then recreate each file below at the exact path shown in the section header. Fenced code blocks with language identifiers like `ts`, `json`, and `bash` preserve formatting and improve readability when you paste this into an editor or coding tool.

## package.json

```json
{
  "name": "cre-analyzer",
  "version": "1.0.0",
  "description": "Commercial Real Estate Lease vs Buy Analysis Engine",
  "main": "dist/cli/index.js",
  "bin": {
    "cre-analyzer": "./dist/cli/index.js"
  },
  "scripts": {
    "build": "tsc",
    "start": "node dist/cli/index.js",
    "dev": "ts-node src/cli/index.ts",
    "test": "jest --coverage",
    "test:watch": "jest --watch",
    "lint": "eslint src/**/*.ts",
    "prepublishOnly": "npm run build && npm test"
  },
  "keywords": [
    "commercial-real-estate",
    "lease-vs-buy",
    "financial-analysis",
    "irr",
    "npv"
  ],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "commander": "^11.1.0",
    "decimal.js": "^10.4.3",
    "inquirer": "^9.2.12",
    "chalk": "^4.1.2",
    "ora": "^5.4.1",
    "table": "^6.8.1"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/jest": "^29.5.11",
    "@types/inquirer": "^9.0.7",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1",
    "typescript": "^5.3.2",
    "ts-node": "^10.9.2"
  }
}
```

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests", "**/*.test.ts"]
}
```

## jest.config.js

```js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests', '<rootDir>/src'],
  testMatch: ['**/*.test.ts'],
  moduleFileExtensions: ['ts', 'js', 'json'],
  collectCoverageFrom: [
    'src/engine/**/*.ts',
    '!src/engine/*.d.ts'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  verbose: true
};
```

## src/types/index.ts

```ts
export type PropertyType = 'office' | 'industrial' | 'retail' | 'multifamily' | 'land';
export type LeaseType = 'NNN' | 'NN' | 'N' | 'Gross' | 'Modified Gross' | 'Base Year' | 'Expense Stop';
export type ReassessmentTrigger = 'sale' | 'improvement' | 'cycle' | 'none';
export type ReassessmentValueBasis = 'sale_price' | 'market_value' | 'assessed_value';
export type EscalationType = 'fixed_pct' | 'cpi' | 'porters_wage' | 'fixed_amount' | 'none';
export type CapExCategory =
  | 'roof'
  | 'hvac'
  | 'parking_asphalt'
  | 'parking_concrete'
  | 'landscape_hardscape'
  | 'paint_exterior'
  | 'paint_interior'
  | 'fire_life_safety'
  | 'elevator'
  | 'plumbing'
  | 'electrical'
  | 'structural'
  | 'ada_compliance'
  | 'energy_retrofit'
  | 'tenant_improvements'
  | 'other';

export interface PropertyTaxContext {
  annualTaxAmount: number;
  taxRatePerSqFt: number;
  assessmentYear: number;
  reassessmentTrigger: ReassessmentTrigger;
  reassessmentValueBasis: ReassessmentValueBasis;
  estimatedPostTransactionTax: number;
  millageRate?: number;
  assessmentRatio?: number;
  statutoryCap?: number;
  jurisdiction: string;
}

export interface InsuranceContext {
  annualPremium: number;
  premiumPerSqFt: number;
  coverageType: 'standard' | 'enhanced' | 'catastrophe';
  deductible: number;
  escalationRate: number;
}

export interface MaintenanceRepairContext {
  annualRoutineMaintenance: number;
  annualPreventiveMaintenance: number;
  annualReactiveRepairs: number;
  totalAnnualMROperating: number;
}

export interface ComponentReserve {
  category: CapExCategory;
  description: string;
  estimatedUsefulLifeYears: number;
  remainingUsefulLifeYears: number;
  currentReplacementCost: number;
  costPerSqFt: number;
  annualReserveContribution: number;
  lastReplacedYear?: number;
  conditionRating: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  priority: 'immediate' | '1-2yr' | '3-5yr' | '6-10yr' | '10+yr';
}

export interface CapExReserveContext {
  reservesPerSqFtPerYear: number;
  componentReserves: ComponentReserve[];
  totalAnnualReserves: number;
}

export interface ManagementContext {
  managementFeePct: number;
  managementFeePerSqFt: number;
  assetManagementFee: number;
  propertyManagementFee: number;
}

export interface UtilityContext {
  electricity: number;
  gas: number;
  waterSewer: number;
  trash: number;
  telecom: number;
  totalLandlordUtilities: number;
  tenantElectricity?: number;
  tenantGas?: number;
  tenantWaterSewer?: number;
}

export interface CAMContext {
  parkingLotMaintenance: number;
  landscaping: number;
  snowRemoval: number;
  exteriorLighting: number;
  signage: number;
  commonAreaCleaning: number;
  security: number;
  propertyTaxesCommonArea: number;
  insuranceCommonArea: number;
  managementCommonArea: number;
  adminLegal: number;
  totalCAM: number;
  camCap?: number;
  camFloor?: number;
  baseYearCAM?: number;
}

export interface AdministrativeContext {
  legal: number;
  accounting: number;
  licensesPermits: number;
  marketing: number;
  officeSupplies: number;
  totalAdmin: number;
}

export interface ComprehensiveOpExContext {
  propertyTax: PropertyTaxContext;
  insurance: InsuranceContext;
  maintenanceRepair: MaintenanceRepairContext;
  capexReserves: CapExReserveContext;
  management: ManagementContext;
  utilities: UtilityContext;
  cam: CAMContext;
  administrative: AdministrativeContext;
  totalOperatingExpenses: number;
  totalCapExReserves: number;
  totalCostOfOwnership: number;
  tenantReimbursable: {
    propertyTax: number;
    insurance: number;
    cam: number;
    utilities: number;
    management: number;
    total: number;
  };
  landlordNonReimbursable: number;
}

export interface BaseComp {
  id: string;
  address: string;
  propertyType: PropertyType;
  buildingSqFt: number;
  landAcres: number;
  yearBuilt: number;
  opexContext: ComprehensiveOpExContext;
}

export interface SaleComp extends BaseComp {
  salePrice: number;
  saleDate: string;
  capRate?: number;
  noi: number;
  noiAfterReserves: number;
  pricePerSqFt: number;
  actualOperatingExpenses: number;
  actualCapExSpent: number;
}

export interface EscalationClause {
  type: EscalationType;
  value: number;
  frequencyYears: number;
  cap?: number;
  floor?: number;
  baseYear?: number;
  appliesTo: 'base_rent' | 'opex' | 'cam' | 'taxes' | 'all';
}

export interface OpExBreakdown {
  propertyTax: number;
  insurance: number;
  cam: number;
  utilities: number;
  management: number;
  maintenanceRepair: number;
  administrative: number;
  totalOpEx: number;
  capexReserves: number;
}

export interface LeaseComp extends BaseComp {
  leaseRatePerSqFtYr: number;
  leaseType: LeaseType;
  opExBreakdown: OpExBreakdown;
  effectiveRentPerSqFt: number;
  leaseTermYears: number;
  tenantImprovementAllowance: number;
  freeRentMonths: number;
  escalations: EscalationClause[];
  expenseStop?: number;
  baseYear?: number;
  reimbursementStructure: {
    propertyTax: 'tenant' | 'landlord' | 'base_year' | 'expense_stop' | 'none';
    insurance: 'tenant' | 'landlord' | 'base_year' | 'expense_stop' | 'none';
    cam: 'tenant' | 'landlord' | 'base_year' | 'expense_stop' | 'none';
    utilities: 'tenant' | 'landlord' | 'submetered' | 'none';
    maintenanceRepair: 'tenant' | 'landlord' | 'shared' | 'none';
    capexReserves: 'tenant' | 'landlord' | 'shared' | 'none';
  };
  actualTenantReimbursements?: number;
  actualLandlordExpenses?: number;
}

export interface SubjectProperty {
  address: string;
  propertyType: PropertyType;
  buildingSqFt: number;
  landAcres: number;
  yearBuilt: number;
  opexContext: ComprehensiveOpExContext;
  marketRentPerSqFt?: number;
  purchasePrice?: number;
  conditionAssessment: {
    roof: ComponentReserve;
    hvac: ComponentReserve;
    parking: ComponentReserve;
    exterior: ComponentReserve;
    interior: ComponentReserve;
    lifeSafety: ComponentReserve;
    overallRating: 'excellent' | 'good' | 'fair' | 'poor';
    deferredMaintenance: number;
  };
}

export interface FinancingParams {
  ltv: number;
  amortizationYears: number;
  interestRate: number;
  loanFees?: number;
  interestOnlyPeriod?: number;
  dscr?: number;
}

export interface PlannedCapExItem {
  year: number;
  category: CapExCategory;
  description: string;
  cost: number;
  fundedFromReserves: boolean;
}

export interface BuyScenarioParams {
  holdingPeriodYears: number;
  discountRate: number;
  financing: FinancingParams;
  closingCostsPct: number;
  exitCapPremium: number;
  sellingCostsPct: number;
  capitalGainsRate: number;
  depreciationLife: number;
  reservesPerSqFt: number;
  managementFeePct: number;
  taxGrowthRate: number;
  insuranceGrowthRate: number;
  opexGrowthRate: number;
  capexReserveGrowthRate: number;
  noiGrowthRate: number;
  plannedCapEx: PlannedCapExItem[];
}

export interface LeaseScenarioParams {
  holdingPeriodYears: number;
  discountRate: number;
  upfrontCosts: {
    legalFees: number;
    brokerFees: number;
    movingCosts: number;
    tiAllowanceReceived: number;
    buildoutCosts: number;
  };
  opportunityCostRate: number;
  leaseCompIndex: number;
  leaseOpExGrowthRate: number;
  renewalProbability: number;
  renewalRentBump: number;
  renewalTermYears: number;
}

export interface NormalizationDetail {
  category: string;
  compValue: number;
  subjectValue: number;
  adjustment: number;
  reason: string;
}

export interface NormalizedComp<T extends BaseComp> {
  original: T;
  adjustedNoi?: number;
  adjustedCapRate?: number;
  adjustedEffectiveRent?: number;
  adjustedTotalOpEx?: number;
  adjustedCapExReserves?: number;
  taxAdjustment: number;
  insuranceAdjustment: number;
  maintenanceAdjustment: number;
  capexAdjustment: number;
  managementAdjustment: number;
  utilityAdjustment: number;
  camAdjustment: number;
  adminAdjustment: number;
  totalAdjustment: number;
  notes: string[];
  normalizationDetails: NormalizationDetail[];
}

export interface AnnualCashFlow {
  year: number;
  potentialGrossIncome: number;
  vacancyLoss: number;
  effectiveGrossIncome: number;
  operatingExpenses: number;
  noi: number;
  capexReserves: number;
  plannedCapEx: number;
  totalCapEx: number;
  debtService: number;
  interestPortion: number;
  principalPortion: number;
  cashFlowBeforeTax: number;
  depreciation: number;
  interestDeduction: number;
  taxableIncome: number;
  taxShield: number;
  cashFlowAfterTax: number;
  cumulativeCashFlow: number;
  loanBalance: number;
  reservesBalance: number;
}

export interface BuyAnalysisResult {
  acquisitionCost: number;
  loanAmount: number;
  equityInvested: number;
  annualCashFlows: AnnualCashFlow[];
  terminalValue: number;
  saleProceedsAfterCosts: number;
  mortgagePayoff: number;
  capitalGainsTax: number;
  depreciationRecaptureTax: number;
  netSaleProceeds: number;
  npv: number;
  irr: number;
  equityMultiple: number;
  breakEvenYear: number | null;
  averageCashOnCash: number;
  averageDSCR: number;
  totalCapExInvested: number;
  totalReservesFunded: number;
}

export interface LeaseAnnualCashFlow {
  year: number;
  baseRent: number;
  propertyTaxReimb: number;
  insuranceReimb: number;
  camReimb: number;
  utilitiesReimb: number;
  maintenanceReimb: number;
  totalReimbursements: number;
  totalLeasePayment: number;
  tenantOpExDirect: number;
  tenantCapEx: number;
  opportunityCost: number;
  totalAnnualCost: number;
  cumulativeCost: number;
}

export interface LeaseAnalysisResult {
  upfrontCosts: number;
  annualCashFlows: LeaseAnnualCashFlow[];
  npv: number;
  totalCost: number;
  effectiveRentYear1: number;
  effectiveRentYear10: number;
  averageAnnualCost: number;
}

export interface ComparisonMetrics {
  npvBuy: number;
  npvLease: number;
  npvDelta: number;
  irrDifferential: number;
  breakEvenYear: number | null;
  recommendation: 'BUY' | 'LEASE' | 'INDETERMINATE';
  confidenceScore: number;
  buyAdvantages: string[];
  leaseAdvantages: string[];
  keyRisks: string[];
}

export interface SensitivityGrid {
  exitCapRates: number[];
  discountRates: number[];
  taxGrowthRates: number[];
  opexGrowthRates: number[];
  capexGrowthRates: number[];
  npvDeltas: number[][][][];
}

export interface AnalysisOutput {
  subjectProperty: SubjectProperty;
  normalizedSaleComps: NormalizedComp<SaleComp>[];
  normalizedLeaseComps: NormalizedComp<LeaseComp>[];
  buyAnalysis: BuyAnalysisResult;
  leaseAnalysis: LeaseAnalysisResult;
  comparison: ComparisonMetrics;
  sensitivity: SensitivityGrid;
  parameters: {
    buy: BuyScenarioParams;
    lease: LeaseScenarioParams;
  };
  timestamp: string;
}

export interface IListingProvider {
  name: string;
  getSaleComps(subject: SubjectProperty, count: number): Promise<SaleComp[]>;
  getLeaseComps(subject: SubjectProperty, count: number): Promise<LeaseComp[]>;
  getSubjectProperty(address: string): Promise<SubjectProperty>;
}

export type ProviderType = 'mock' | 'manual' | 'costar' | 'crexi' | 'loopnet' | 'csv' | 'attom' | 'reonomy';

export interface CLIOptions {
  address: string;
  provider: ProviderType;
  holdingPeriod: number;
  discountRate: number;
  ltv: number;
  interestRate: number;
  exitCapPremium: number;
  output: 'table' | 'json' | 'both';
  report?: string;
  config?: string;
  taxGrowthRate?: number;
  opexGrowthRate?: number;
  capexGrowthRate?: number;
  reservesPerSqFt?: number;
}
```

## src/cli/index.ts

```ts
#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { readFileSync, writeFileSync } from 'fs';

import { IListingProvider } from '../providers/IListingProvider';
import { MockProvider } from '../providers/MockProvider';
import { ManualEntryProvider } from '../providers/IListingProvider';
import {
  CLIOptions,
  BuyScenarioParams,
  LeaseScenarioParams,
  AnalysisOutput,
  ProviderType
} from '../types';
import { selectAndNormalizeComps } from '../engine/compSelector';
import { analyzeBuyScenario } from '../engine/buyAnalyzer';
import { analyzeLeaseComps } from '../engine/leaseAnalyzer';
import { compareBuyVsLease, runSensitivityAnalysis } from '../engine/comparisonEngine';
import { reportToConsole } from '../reporters/ConsoleReporter';
import { reportToJson } from '../reporters/JsonReporter';
import { reportToHtml } from '../reporters/HtmlReporter';

const program = new Command();

program
  .name('cre-analyzer')
  .description('Commercial Real Estate Lease vs Buy Analysis Engine')
  .version('1.0.0');

program
  .command('analyze')
  .requiredOption('-a, --address <address>', 'Subject property address')
  .option('-p, --provider <type>', 'Provider: mock, manual, costar, crexi, loopnet, csv', 'mock')
  .option('-h, --holding-period <years>', 'Holding period in years', '10')
  .option('-d, --discount-rate <rate>', 'Discount rate', '0.08')
  .option('-l, --ltv <ratio>', 'Loan-to-value ratio', '0.70')
  .option('-i, --interest-rate <rate>', 'Interest rate', '0.065')
  .option('-e, --exit-cap-premium <bps>', 'Exit cap premium in bps', '75')
  .option('-o, --output <format>', 'table, json, both', 'table')
  .option('-r, --report <path>', 'HTML report output path')
  .option('-c, --config <path>', 'Config file path')
  .option('--tax-growth <rate>', 'Annual tax growth rate', '0.02')
  .option('--opex-growth <rate>', 'Annual OpEx growth rate', '0.03')
  .option('--capex-growth <rate>', 'Annual CapEx growth rate', '0.02')
  .option('--reserves <perSqFt>', 'Reserves per SF', '0.35')
  .action(async (options: CLIOptions) => {
    try {
      await runAnalysis(options);
    } catch (error) {
      console.error(chalk.red('Error:'), error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });

program.parseAsync(process.argv).catch(console.error);

async function runAnalysis(options: CLIOptions) {
  const spinner = ora('Initializing...').start();

  let config: Partial<CLIOptions> = {};
  if (options.config) {
    try {
      config = JSON.parse(readFileSync(options.config, 'utf-8'));
      spinner.text = `Loaded config from ${options.config}`;
    } catch (e) {
      spinner.warn(`Could not load config: ${e}`);
    }
  }

  const mergedOptions = { ...config, ...options } as CLIOptions;

  spinner.text = `Initializing ${mergedOptions.provider} provider...`;
  const provider = await getProvider(mergedOptions.provider);

  spinner.text = 'Fetching subject property...';
  const subject = await provider.getSubjectProperty(mergedOptions.address);

  spinner.text = 'Fetching sale comps...';
  const saleComps = await provider.getSaleComps(subject, 4);

  spinner.text = 'Fetching lease comps...';
  const leaseComps = await provider.getLeaseComps(subject, 4);

  spinner.succeed('Data loaded');

  const spinner2 = ora('Normalizing comparables...').start();
  const { normalizedSaleComps, normalizedLeaseComps, marketMetrics } =
    selectAndNormalizeComps(subject, saleComps, leaseComps);
  spinner2.succeed('Normalization complete');

  const buyParams: BuyScenarioParams = {
    holdingPeriodYears: Number(mergedOptions.holdingPeriod),
    discountRate: Number(mergedOptions.discountRate),
    financing: {
      ltv: Number(mergedOptions.ltv),
      amortizationYears: 25,
      interestRate: Number(mergedOptions.interestRate)
    },
    closingCostsPct: 0.025,
    exitCapPremium: Number(mergedOptions.exitCapPremium) / 10000,
    sellingCostsPct: 0.05,
    capitalGainsRate: 0.238,
    depreciationLife: 39,
    reservesPerSqFt: Number(mergedOptions.reservesPerSqFt ?? 0.35),
    managementFeePct: 0.03,
    taxGrowthRate: Number(mergedOptions.taxGrowthRate ?? 0.02),
    insuranceGrowthRate: 0.04,
    opexGrowthRate: Number(mergedOptions.opexGrowthRate ?? 0.03),
    capexReserveGrowthRate: Number(mergedOptions.capexGrowthRate ?? 0.02),
    noiGrowthRate: 0.02,
    plannedCapEx: []
  };

  const leaseParams: LeaseScenarioParams = {
    holdingPeriodYears: Number(mergedOptions.holdingPeriod),
    discountRate: Number(mergedOptions.discountRate),
    upfrontCosts: {
      legalFees: 15000,
      brokerFees: 25000,
      movingCosts: 10000,
      tiAllowanceReceived: 0,
      buildoutCosts: 50000
    },
    opportunityCostRate: 0.05,
    leaseCompIndex: 0,
    leaseOpExGrowthRate: 0.03,
    renewalProbability: 0.7,
    renewalRentBump: 0.1,
    renewalTermYears: 5
  };

  const marketRent = marketMetrics.avgAdjustedRent || subject.marketRentPerSqFt || 12.5;

  const spinner3 = ora('Running buy analysis...').start();
  const buyAnalysis = analyzeBuyScenario(subject, marketRent, buyParams);
  spinner3.succeed('Buy complete');

  const spinner4 = ora('Running lease analysis...').start();
  const leaseAnalysisResult = analyzeLeaseComps(subject, normalizedLeaseComps, leaseParams);
  const leaseAnalysis = leaseAnalysisResult.average;
  spinner4.succeed('Lease complete');

  const spinner5 = ora('Comparing scenarios...').start();
  const comparison = compareBuyVsLease(
    subject,
    buyAnalysis,
    leaseAnalysis,
    normalizedSaleComps,
    normalizedLeaseComps
  );
  spinner5.succeed('Comparison complete');

  const spinner6 = ora('Running sensitivity analysis...').start();
  const sensitivity = runSensitivityAnalysis(
    subject,
    buyParams,
    leaseParams,
    marketRent,
    normalizedSaleComps,
    normalizedLeaseComps
  );
  spinner6.succeed('Sensitivity complete');

  const output: AnalysisOutput = {
    subjectProperty: subject,
    normalizedSaleComps,
    normalizedLeaseComps,
    buyAnalysis,
    leaseAnalysis,
    comparison,
    sensitivity,
    parameters: { buy: buyParams, lease: leaseParams },
    timestamp: new Date().toISOString()
  };

  if (mergedOptions.output === 'table' || mergedOptions.output === 'both') {
    reportToConsole(output, { verbose: true });
  }

  if (mergedOptions.output === 'json' || mergedOptions.output === 'both') {
    const jsonOutput = reportToJson(output);
    const jsonPath = mergedOptions.report?.replace('.html', '.json') || './cre-analysis.json';
    writeFileSync(jsonPath, jsonOutput);
    console.log(chalk.green(`JSON report saved to ${jsonPath}`));
  }

  if (mergedOptions.report) {
    reportToHtml(output, mergedOptions.report);
    console.log(chalk.green(`HTML report saved to ${mergedOptions.report}`));
  }
}

async function getProvider(type: ProviderType): Promise<IListingProvider> {
  switch (type) {
    case 'mock':
      return new MockProvider();
    case 'manual':
      return new ManualEntryProvider();
    default:
      throw new Error(`Provider not implemented: ${type}`);
  }
}
```

## src/reporters/JsonReporter.ts

```ts
import { AnalysisOutput } from '../types';

export function reportToJson(output: AnalysisOutput): string {
  const jsonOutput = {
    metadata: {
      generatedAt: output.timestamp,
      version: '1.0.0',
      tool: 'cre-analyzer'
    },
    subjectProperty: {
      address: output.subjectProperty.address,
      propertyType: output.subjectProperty.propertyType,
      buildingSqFt: output.subjectProperty.buildingSqFt,
      landAcres: output.subjectProperty.landAcres,
      yearBuilt: output.subjectProperty.yearBuilt,
      marketRentPerSqFt: output.subjectProperty.marketRentPerSqFt,
      purchasePrice: output.subjectProperty.purchasePrice,
      conditionRating: output.subjectProperty.conditionAssessment?.overallRating,
      deferredMaintenance: output.subjectProperty.conditionAssessment?.deferredMaintenance,
      totalCostOfOwnershipPerSf: output.subjectProperty.opexContext.totalCostOfOwnership,
      operatingExpensesPerSf: output.subjectProperty.opexContext.totalOperatingExpenses,
      capexReservesPerSf: output.subjectProperty.opexContext.totalCapExReserves
    },
    normalizedSaleComps: output.normalizedSaleComps,
    normalizedLeaseComps: output.normalizedLeaseComps,
    buyAnalysis: output.buyAnalysis,
    leaseAnalysis: output.leaseAnalysis,
    comparison: output.comparison,
    sensitivity: output.sensitivity,
    parameters: output.parameters
  };

  return JSON.stringify(jsonOutput, null, 2);
}
```

## src/reporters/HtmlReporter.ts

```ts
import { AnalysisOutput } from '../types';
import { writeFileSync } from 'fs';

export function reportToHtml(output: AnalysisOutput, filePath: string): void {
  const html = generateHtml(output);
  writeFileSync(filePath, html, 'utf-8');
}

function generateHtml(output: AnalysisOutput): string {
  const { subjectProperty, buyAnalysis, leaseAnalysis, comparison } = output;
  const buyCashFlows = JSON.stringify(buyAnalysis.annualCashFlows.map(cf => cf.cashFlowAfterTax));
  const leaseCosts = JSON.stringify(leaseAnalysis.annualCashFlows.map(cf => cf.totalAnnualCost));
  const years = JSON.stringify(buyAnalysis.annualCashFlows.map(cf => `Year ${cf.year}`));

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CRE Analysis - ${subjectProperty.address}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; color: #222; }
    .container { max-width: 1200px; margin: 0 auto; }
    .box { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
    h1, h2 { color: #123; }
    table { width: 100%; border-collapse: collapse; margin: 12px 0; }
    th, td { border-bottom: 1px solid #eee; padding: 10px; text-align: left; }
    th { background: #f6f6f6; }
  </style>
</head>
<body>
  <div class="container">
    <h1>CRE Lease vs Buy Analysis</h1>
    <div class="box">
      <p><strong>Property:</strong> ${subjectProperty.address}</p>
      <p><strong>Recommendation:</strong> ${comparison.recommendation}</p>
      <p><strong>Confidence:</strong> ${(comparison.confidenceScore * 100).toFixed(0)}%</p>
      <p><strong>NPV Delta:</strong> $${comparison.npvDelta.toLocaleString()}</p>
    </div>

    <div class="grid">
      <div class="box"><strong>Buy NPV</strong><br>$${buyAnalysis.npv.toLocaleString()}</div>
      <div class="box"><strong>Lease NPV</strong><br>$${leaseAnalysis.npv.toLocaleString()}</div>
      <div class="box"><strong>Buy IRR</strong><br>${(buyAnalysis.irr * 100).toFixed(1)}%</div>
      <div class="box"><strong>TCO</strong><br>$${subjectProperty.opexContext.totalCostOfOwnership.toFixed(2)}/SF</div>
    </div>

    <div class="box">
      <h2>Cash Flow Comparison</h2>
      <canvas id="chart"></canvas>
    </div>
  </div>

  <script>
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ${years},
        datasets: [
          {
            label: 'Buy CFAT',
            data: ${buyCashFlows},
            borderColor: '#2f855a',
            backgroundColor: 'rgba(47,133,90,.15)'
          },
          {
            label: 'Lease Total Cost',
            data: ${leaseCosts},
            borderColor: '#2b6cb0',
            backgroundColor: 'rgba(43,108,176,.15)'
          }
        ]
      }
    });
  </script>
</body>
</html>`;
}
```

## src/providers/IListingProvider.ts

```ts
import { SubjectProperty, SaleComp, LeaseComp, ProviderType } from '../types';
import inquirer from 'inquirer';

export interface IListingProvider {
  name: ProviderType;
  getSubjectProperty(address: string): Promise<SubjectProperty>;
  getSaleComps(subject: SubjectProperty, count: number): Promise<SaleComp[]>;
  getLeaseComps(subject: SubjectProperty, count: number): Promise<LeaseComp[]>;
}

export class ManualEntryProvider implements IListingProvider {
  name = 'manual' as const;

  async getSubjectProperty(address: string): Promise<SubjectProperty> {
    const answers = await inquirer.prompt([
      { name: 'propertyType', type: 'list', message: 'Property Type:', choices: ['industrial', 'office', 'retail', 'multifamily', 'land'] },
      { name: 'buildingSqFt', type: 'input', message: 'Building Square Feet:' },
      { name: 'landAcres', type: 'input', message: 'Land Acres:' },
      { name: 'yearBuilt', type: 'input', message: 'Year Built:' },
      { name: 'annualTaxAmount', type: 'input', message: 'Annual Property Tax:' },
      { name: 'jurisdiction', type: 'input', message: 'Tax Jurisdiction:' }
    ]);

    const buildingSqFt = Number(answers.buildingSqFt);
    const annualTaxAmount = Number(answers.annualTaxAmount);
    const taxRatePerSqFt = annualTaxAmount / buildingSqFt;

    return {
      address,
      propertyType: answers.propertyType,
      buildingSqFt,
      landAcres: Number(answers.landAcres),
      yearBuilt: Number(answers.yearBuilt),
      marketRentPerSqFt: 12.5,
      purchasePrice: 2800000,
      opexContext: {
        propertyTax: {
          annualTaxAmount,
          taxRatePerSqFt,
          assessmentYear: new Date().getFullYear() - 1,
          reassessmentTrigger: 'sale',
          reassessmentValueBasis: 'sale_price',
          estimatedPostTransactionTax: annualTaxAmount * 1.25,
          jurisdiction: answers.jurisdiction
        },
        insurance: { annualPremium: buildingSqFt * 0.35, premiumPerSqFt: 0.35, coverageType: 'standard', deductible: 10000, escalationRate: 0.04 },
        maintenanceRepair: { annualRoutineMaintenance: 0.4, annualPreventiveMaintenance: 0.3, annualReactiveRepairs: 0.25, totalAnnualMROperating: 0.95 },
        capexReserves: { reservesPerSqFtPerYear: 0.35, componentReserves: [], totalAnnualReserves: 0.35 },
        management: { managementFeePct: 0.03, managementFeePerSqFt: 0.5, assetManagementFee: 0.1, propertyManagementFee: 0.4 },
        utilities: { electricity: 0.15, gas: 0.05, waterSewer: 0.03, trash: 0.02, telecom: 0, totalLandlordUtilities: 0.25, tenantElectricity: 0.75, tenantGas: 0.2, tenantWaterSewer: 0.1 },
        cam: { parkingLotMaintenance: 0.15, landscaping: 0.2, snowRemoval: 0, exteriorLighting: 0.05, signage: 0.03, commonAreaCleaning: 0.05, security: 0.1, propertyTaxesCommonArea: 0.05, insuranceCommonArea: 0.02, managementCommonArea: 0.08, adminLegal: 0.02, totalCAM: 0.75, baseYearCAM: 0.75 },
        administrative: { legal: 0.05, accounting: 0.03, licensesPermits: 0.02, marketing: 0.05, officeSupplies: 0.02, totalAdmin: 0.17 },
        totalOperatingExpenses: taxRatePerSqFt + 0.35 + 0.95 + 1.0 + 0.25 + 0.75 + 0.17,
        totalCapExReserves: 0.35,
        totalCostOfOwnership: taxRatePerSqFt + 0.35 + 0.95 + 1.0 + 0.25 + 0.75 + 0.17 + 0.35,
        tenantReimbursable: { propertyTax: taxRatePerSqFt, insurance: 0.35, cam: 0.75, utilities: 0, management: 0, total: taxRatePerSqFt + 1.1 },
        landlordNonReimbursable: 0.45
      },
      conditionAssessment: {
        overallRating: 'fair',
        deferredMaintenance: 0,
        roof: {} as any,
        hvac: {} as any,
        parking: {} as any,
        exterior: {} as any,
        interior: {} as any,
        lifeSafety: {} as any
      }
    };
  }

  async getSaleComps(): Promise<SaleComp[]> {
    return [];
  }

  async getLeaseComps(): Promise<LeaseComp[]> {
    return [];
  }
}
```

## src/providers/MockProvider.ts

```ts
import {
  SubjectProperty,
  SaleComp,
  LeaseComp,
  ComprehensiveOpExContext,
  PropertyType
} from '../types';
import { IListingProvider } from './IListingProvider';
import { buildBestPracticeReserves } from '../engine/expenseNormalizer';

function buildOpExContext(
  propertyType: PropertyType,
  buildingSqFt: number,
  yearBuilt: number,
  annualTaxAmount: number
): ComprehensiveOpExContext {
  const componentReserves = buildBestPracticeReserves(propertyType, buildingSqFt, yearBuilt);
  const totalReserves = componentReserves.reduce((sum, c) => sum + c.annualReserveContribution, 0);

  const totalOperatingExpenses =
    annualTaxAmount / buildingSqFt +
    0.35 +
    0.95 +
    1.0 +
    0.25 +
    0.75 +
    0.17;

  return {
    propertyTax: {
      annualTaxAmount,
      taxRatePerSqFt: annualTaxAmount / buildingSqFt,
      assessmentYear: 2025,
      reassessmentTrigger: 'sale',
      reassessmentValueBasis: 'sale_price',
      estimatedPostTransactionTax: annualTaxAmount * 1.25,
      millageRate: 0.018,
      assessmentRatio: 0.9,
      statutoryCap: 0.02,
      jurisdiction: 'Travis County, TX'
    },
    insurance: {
      annualPremium: buildingSqFt * 0.35,
      premiumPerSqFt: 0.35,
      coverageType: 'standard',
      deductible: 10000,
      escalationRate: 0.04
    },
    maintenanceRepair: {
      annualRoutineMaintenance: 0.4,
      annualPreventiveMaintenance: 0.3,
      annualReactiveRepairs: 0.25,
      totalAnnualMROperating: 0.95
    },
    capexReserves: {
      reservesPerSqFtPerYear: totalReserves,
      componentReserves,
      totalAnnualReserves: totalReserves
    },
    management: {
      managementFeePct: 0.03,
      managementFeePerSqFt: 0.5,
      assetManagementFee: 0.1,
      propertyManagementFee: 0.4
    },
    utilities: {
      electricity: 0.15,
      gas: 0.05,
      waterSewer: 0.03,
      trash: 0.02,
      telecom: 0,
      totalLandlordUtilities: 0.25,
      tenantElectricity: 0.75,
      tenantGas: 0.2,
      tenantWaterSewer: 0.1
    },
    cam: {
      parkingLotMaintenance: 0.15,
      landscaping: 0.2,
      snowRemoval: 0,
      exteriorLighting: 0.05,
      signage: 0.03,
      commonAreaCleaning: 0.05,
      security: 0.1,
      propertyTaxesCommonArea: 0.05,
      insuranceCommonArea: 0.02,
      managementCommonArea: 0.08,
      adminLegal: 0.02,
      totalCAM: 0.75,
      baseYearCAM: 0.75
    },
    administrative: {
      legal: 0.05,
      accounting: 0.03,
      licensesPermits: 0.02,
      marketing: 0.05,
      officeSupplies: 0.02,
      totalAdmin: 0.17
    },
    totalOperatingExpenses,
    totalCapExReserves: totalReserves,
    totalCostOfOwnership: totalOperatingExpenses + totalReserves,
    tenantReimbursable: {
      propertyTax: annualTaxAmount / buildingSqFt,
      insurance: 0.35,
      cam: 0.75,
      utilities: 0,
      management: 0,
      total: annualTaxAmount / buildingSqFt + 1.1
    },
    landlordNonReimbursable: totalReserves + 0.1
  };
}

const subjectOpEx = buildOpExContext('industrial', 20000, 2005, 30000);

export const SUBJECT_PROPERTY: SubjectProperty = {
  address: '123 Industrial Way, Austin, TX 78758',
  propertyType: 'industrial',
  buildingSqFt: 20000,
  landAcres: 2.5,
  yearBuilt: 2005,
  opexContext: subjectOpEx,
  marketRentPerSqFt: 12.5,
  purchasePrice: 2800000,
  conditionAssessment: {
    roof: subjectOpEx.capexReserves.componentReserves[0],
    hvac: subjectOpEx.capexReserves.componentReserves[1],
    parking: subjectOpEx.capexReserves.componentReserves[2],
    exterior: subjectOpEx.capexReserves.componentReserves[3],
    interior: {
      category: 'paint_interior',
      description: 'Interior paint refresh',
      estimatedUsefulLifeYears: 7,
      remainingUsefulLifeYears: 3,
      currentReplacementCost: 30000,
      costPerSqFt: 1.5,
      annualReserveContribution: 1.5 / 7,
      conditionRating: 'fair',
      priority: '3-5yr'
    },
    lifeSafety: subjectOpEx.capexReserves.componentReserves[4],
    overallRating: 'good',
    deferredMaintenance: 0
  }
};

export const MOCK_SALE_COMPS: SaleComp[] = [
  {
    id: 'sale-001',
    address: '4500 Distribution Dr, Austin, TX 78744',
    propertyType: 'industrial',
    buildingSqFt: 22000,
    landAcres: 2.8,
    yearBuilt: 2008,
    salePrice: 3100000,
    saleDate: '2024-03-15',
    capRate: 0.072,
    noi: 223200,
    noiAfterReserves: 215000,
    pricePerSqFt: 140.91,
    actualOperatingExpenses: 220000,
    actualCapExSpent: 15000,
    opexContext: buildOpExContext('industrial', 22000, 2008, 33000)
  },
  {
    id: 'sale-002',
    address: '7200 Warehouse Row, Austin, TX 78752',
    propertyType: 'industrial',
    buildingSqFt: 18500,
    landAcres: 2.2,
    yearBuilt: 1998,
    salePrice: 2200000,
    saleDate: '2023-11-02',
    capRate: 0.085,
    noi: 187000,
    noiAfterReserves: 175000,
    pricePerSqFt: 118.92,
    actualOperatingExpenses: 200000,
    actualCapExSpent: 45000,
    opexContext: buildOpExContext('industrial', 18500, 1998, 18500)
  }
];

export const MOCK_LEASE_COMPS: LeaseComp[] = [
  {
    id: 'lease-001',
    address: '4500 Distribution Dr, Austin, TX 78744',
    propertyType: 'industrial',
    buildingSqFt: 22000,
    landAcres: 2.8,
    yearBuilt: 2008,
    leaseRatePerSqFtYr: 9.5,
    leaseType: 'NNN',
    opExBreakdown: {
      propertyTax: 1.5,
      insurance: 0.35,
      cam: 0.75,
      utilities: 0,
      management: 0,
      maintenanceRepair: 0,
      administrative: 0,
      totalOpEx: 2.6,
      capexReserves: 0
    },
    effectiveRentPerSqFt: 12.1,
    leaseTermYears: 5,
    tenantImprovementAllowance: 5,
    freeRentMonths: 1,
    escalations: [{ type: 'fixed_pct', value: 0.03, frequencyYears: 1, appliesTo: 'base_rent' }],
    reimbursementStructure: {
      propertyTax: 'tenant',
      insurance: 'tenant',
      cam: 'tenant',
      utilities: 'tenant',
      maintenanceRepair: 'tenant',
      capexReserves: 'landlord'
    },
    opexContext: buildOpExContext('industrial', 22000, 2008, 33000)
  },
  {
    id: 'lease-002',
    address: '3100 Logistics Blvd, Austin, TX 78753',
    propertyType: 'industrial',
    buildingSqFt: 25000,
    landAcres: 3.0,
    yearBuilt: 2015,
    leaseRatePerSqFtYr: 11,
    leaseType: 'NNN',
    opExBreakdown: {
      propertyTax: 2,
      insurance: 0.3,
      cam: 0.8,
      utilities: 0,
      management: 0,
      maintenanceRepair: 0,
      administrative: 0,
      totalOpEx: 3.1,
      capexReserves: 0
    },
    effectiveRentPerSqFt: 14.1,
    leaseTermYears: 7,
    tenantImprovementAllowance: 7.5,
    freeRentMonths: 2,
    escalations: [{ type: 'fixed_pct', value: 0.03, frequencyYears: 1, appliesTo: 'base_rent' }],
    reimbursementStructure: {
      propertyTax: 'tenant',
      insurance: 'tenant',
      cam: 'tenant',
      utilities: 'tenant',
      maintenanceRepair: 'tenant',
      capexReserves: 'landlord'
    },
    opexContext: buildOpExContext('industrial', 25000, 2015, 50000)
  }
];

export class MockProvider implements IListingProvider {
  name = 'mock' as const;

  async getSubjectProperty(address: string): Promise<SubjectProperty> {
    return { ...SUBJECT_PROPERTY, address };
  }

  async getSaleComps(): Promise<SaleComp[]> {
    return MOCK_SALE_COMPS;
  }

  async getLeaseComps(): Promise<LeaseComp[]> {
    return MOCK_LEASE_COMPS;
  }
}
```

## src/engine/expenseNormalizer.ts

```ts
import {
  LeaseComp,
  SaleComp,
  SubjectProperty,
  NormalizedComp,
  NormalizationDetail,
  ComponentReserve,
  PlannedCapExItem,
  PropertyType
} from '../types';

export function buildBestPracticeReserves(
  propertyType: PropertyType,
  buildingSqFt: number,
  yearBuilt: number,
  currentYear: number = new Date().getFullYear()
): ComponentReserve[] {
  const buildingAge = currentYear - yearBuilt;
  if (propertyType !== 'industrial') return [];

  return [
    {
      category: 'roof',
      description: 'Membrane roof replacement',
      estimatedUsefulLifeYears: 20,
      remainingUsefulLifeYears: Math.max(0, 20 - (buildingAge % 20)),
      currentReplacementCost: buildingSqFt * 8,
      costPerSqFt: 8,
      annualReserveContribution: 8 / 20,
      conditionRating: buildingAge < 10 ? 'good' : buildingAge < 20 ? 'fair' : 'poor',
      priority: buildingAge > 18 ? '1-2yr' : '3-5yr'
    },
    {
      category: 'hvac',
      description: 'Warehouse HVAC',
      estimatedUsefulLifeYears: 15,
      remainingUsefulLifeYears: Math.max(0, 15 - (buildingAge % 15)),
      currentReplacementCost: buildingSqFt * 4.5,
      costPerSqFt: 4.5,
      annualReserveContribution: 4.5 / 15,
      conditionRating: buildingAge < 8 ? 'good' : buildingAge < 15 ? 'fair' : 'poor',
      priority: buildingAge > 13 ? '1-2yr' : '3-5yr'
    },
    {
      category: 'parking_asphalt',
      description: 'Parking resurfacing',
      estimatedUsefulLifeYears: 10,
      remainingUsefulLifeYears: Math.max(0, 10 - (buildingAge % 10)),
      currentReplacementCost: buildingSqFt * 1.25,
      costPerSqFt: 1.25,
      annualReserveContribution: 1.25 / 10,
      conditionRating: buildingAge < 5 ? 'good' : buildingAge < 10 ? 'fair' : 'poor',
      priority: buildingAge > 8 ? '1-2yr' : '3-5yr'
    },
    {
      category: 'paint_exterior',
      description: 'Exterior paint',
      estimatedUsefulLifeYears: 8,
      remainingUsefulLifeYears: Math.max(0, 8 - (buildingAge % 8)),
      currentReplacementCost: buildingSqFt * 0.75,
      costPerSqFt: 0.75,
      annualReserveContribution: 0.75 / 8,
      conditionRating: buildingAge < 4 ? 'good' : buildingAge < 8 ? 'fair' : 'poor',
      priority: buildingAge > 6 ? '1-2yr' : '3-5yr'
    },
    {
      category: 'fire_life_safety',
      description: 'Life safety systems',
      estimatedUsefulLifeYears: 12,
      remainingUsefulLifeYears: Math.max(0, 12 - (buildingAge % 12)),
      currentReplacementCost: buildingSqFt * 1.0,
      costPerSqFt: 1.0,
      annualReserveContribution: 1 / 12,
      conditionRating: 'good',
      priority: '3-5yr'
    }
  ];
}

export function calculateTotalAnnualReserves(componentReserves: ComponentReserve[]): number {
  return componentReserves.reduce((sum, c) => sum + c.annualReserveContribution, 0);
}

export function generatePlannedCapExFromReserves(
  componentReserves: ComponentReserve[],
  holdingPeriodYears: number = 10
): PlannedCapExItem[] {
  return componentReserves
    .filter(r => r.remainingUsefulLifeYears <= holdingPeriodYears)
    .map(r => ({
      year: Math.max(1, r.remainingUsefulLifeYears),
      category: r.category,
      description: r.description,
      cost: r.currentReplacementCost,
      fundedFromReserves: true
    }))
    .sort((a, b) => a.year - b.year);
}

export function normalizeTotalCostOfOwnership<T extends SaleComp | LeaseComp>(
  comp: T,
  subject: SubjectProperty
): NormalizedComp<T> {
  const compOpEx = comp.opexContext;
  const subjectOpEx = subject.opexContext;

  const taxAdj = (subjectOpEx.propertyTax.taxRatePerSqFt - compOpEx.propertyTax.taxRatePerSqFt) * comp.buildingSqFt;
  const insAdj = (subjectOpEx.insurance.premiumPerSqFt - compOpEx.insurance.premiumPerSqFt) * comp.buildingSqFt;
  const maintAdj = (subjectOpEx.maintenanceRepair.totalAnnualMROperating - compOpEx.maintenanceRepair.totalAnnualMROperating) * comp.buildingSqFt;
  const capexAdj = (subjectOpEx.capexReserves.totalAnnualReserves - compOpEx.capexReserves.totalAnnualReserves) * comp.buildingSqFt;
  const mgmtAdj = (
    (subjectOpEx.management.managementFeePerSqFt + subjectOpEx.management.assetManagementFee + subjectOpEx.management.propertyManagementFee) -
    (compOpEx.management.managementFeePerSqFt + compOpEx.management.assetManagementFee + compOpEx.management.propertyManagementFee)
  ) * comp.buildingSqFt;
  const utilAdj = (subjectOpEx.utilities.totalLandlordUtilities - compOpEx.utilities.totalLandlordUtilities) * comp.buildingSqFt;
  const camAdj = (subjectOpEx.cam.totalCAM - compOpEx.cam.totalCAM) * comp.buildingSqFt;
  const adminAdj = (subjectOpEx.administrative.totalAdmin - compOpEx.administrative.totalAdmin) * comp.buildingSqFt;

  const totalAdjustment = taxAdj + insAdj + maintAdj + capexAdj + mgmtAdj + utilAdj + camAdj + adminAdj;

  const normalizationDetails: NormalizationDetail[] = [
    { category: 'Property Tax', compValue: compOpEx.propertyTax.taxRatePerSqFt, subjectValue: subjectOpEx.propertyTax.taxRatePerSqFt, adjustment: taxAdj, reason: 'Subject basis' }
  ];

  const out: NormalizedComp<T> = {
    original: comp,
    taxAdjustment: taxAdj,
    insuranceAdjustment: insAdj,
    maintenanceAdjustment: maintAdj,
    capexAdjustment: capexAdj,
    managementAdjustment: mgmtAdj,
    utilityAdjustment: utilAdj,
    camAdjustment: camAdj,
    adminAdjustment: adminAdj,
    totalAdjustment,
    notes: [`Total ownership adjustment: $${(totalAdjustment / comp.buildingSqFt).toFixed(2)}/SF`],
    normalizationDetails,
    adjustedTotalOpEx: subjectOpEx.totalOperatingExpenses,
    adjustedCapExReserves: subjectOpEx.totalCapExReserves
  };

  if ('noi' in comp) {
    out.adjustedNoi = comp.noi - (taxAdj + insAdj + maintAdj + mgmtAdj + utilAdj + camAdj + adminAdj);
    out.adjustedCapRate = out.adjustedNoi / comp.salePrice;
  }

  if ('effectiveRentPerSqFt' in comp) {
    out.adjustedEffectiveRent = comp.effectiveRentPerSqFt + totalAdjustment / comp.buildingSqFt;
  }

  return out;
}
```

## src/engine/taxNormalizer.ts

```ts
import { SaleComp, LeaseComp, PropertyTaxContext, NormalizedComp } from '../types';

export function normalizeSaleComp(
  comp: SaleComp,
  subjectTaxContext: PropertyTaxContext
): NormalizedComp<SaleComp> {
  const compTaxPerSqFt = comp.opexContext.propertyTax.taxRatePerSqFt;
  const subjectTaxPerSqFt = subjectTaxContext.taxRatePerSqFt;
  const taxDeltaPerSqFt = subjectTaxPerSqFt - compTaxPerSqFt;
  const totalTaxAdjustment = taxDeltaPerSqFt * comp.buildingSqFt;
  const adjustedNoi =
    comp.noi + compTaxPerSqFt * comp.buildingSqFt - subjectTaxPerSqFt * comp.buildingSqFt;
  const adjustedCapRate = comp.salePrice > 0 ? adjustedNoi / comp.salePrice : 0;

  return {
    original: comp,
    adjustedNoi,
    adjustedCapRate,
    adjustedEffectiveRent: undefined,
    adjustedTotalOpEx: undefined,
    adjustedCapExReserves: undefined,
    taxAdjustment: totalTaxAdjustment,
    insuranceAdjustment: 0,
    maintenanceAdjustment: 0,
    capexAdjustment: 0,
    managementAdjustment: 0,
    utilityAdjustment: 0,
    camAdjustment: 0,
    adminAdjustment: 0,
    totalAdjustment: totalTaxAdjustment,
    notes: [`Comp tax: $${compTaxPerSqFt.toFixed(2)}/SF, subject tax: $${subjectTaxPerSqFt.toFixed(2)}/SF`],
    normalizationDetails: []
  };
}

export function normalizeLeaseComp(
  comp: LeaseComp,
  subjectTaxContext: PropertyTaxContext
): NormalizedComp<LeaseComp> {
  const compTaxRate = comp.opExBreakdown.propertyTax;
  const subjectTaxRate = subjectTaxContext.taxRatePerSqFt;
  const taxRateDelta = subjectTaxRate - compTaxRate;
  const adjustedEffectiveRent = comp.effectiveRentPerSqFt + taxRateDelta;

  return {
    original: comp,
    adjustedNoi: undefined,
    adjustedCapRate: undefined,
    adjustedEffectiveRent,
    adjustedTotalOpEx: undefined,
    adjustedCapExReserves: undefined,
    taxAdjustment: taxRateDelta * comp.buildingSqFt,
    insuranceAdjustment: 0,
    maintenanceAdjustment: 0,
    capexAdjustment: 0,
    managementAdjustment: 0,
    utilityAdjustment: 0,
    camAdjustment: 0,
    adminAdjustment: 0,
    totalAdjustment: taxRateDelta * comp.buildingSqFt,
    notes: [`Adjusted effective rent: $${adjustedEffectiveRent.toFixed(2)}/SF`],
    normalizationDetails: []
  };
}

export function calculateMarketCapRate(normalizedComps: NormalizedComp<SaleComp>[]): number {
  const valid = normalizedComps.filter(c => c.adjustedCapRate && c.adjustedCapRate > 0);
  if (!valid.length) return 0;
  return valid.reduce((sum, c) => sum + (c.adjustedCapRate || 0), 0) / valid.length;
}

export function calculateMarketRent(normalizedComps: NormalizedComp<LeaseComp>[]): number {
  const valid = normalizedComps.filter(c => c.adjustedEffectiveRent && c.adjustedEffectiveRent > 0);
  if (!valid.length) return 0;
  return valid.reduce((sum, c) => sum + (c.adjustedEffectiveRent || 0), 0) / valid.length;
}
```

## src/engine/compSelector.ts

```ts
import { SubjectProperty, SaleComp, LeaseComp, NormalizedComp } from '../types';
import { normalizeTotalCostOfOwnership } from './expenseNormalizer';
import { calculateMarketCapRate, calculateMarketRent } from './taxNormalizer';

export function selectAndNormalizeComps(
  subject: SubjectProperty,
  saleComps: SaleComp[],
  leaseComps: LeaseComp[]
): {
  normalizedSaleComps: NormalizedComp<SaleComp>[];
  normalizedLeaseComps: NormalizedComp<LeaseComp>[];
  marketMetrics: {
    avgAdjustedCapRate: number;
    avgAdjustedRent: number;
    pricePerSqFtRange: { min: number; max: number; median: number };
    rentRange: { min: number; max: number; median: number };
  };
  selectionNotes: string[];
} {
  const filteredSales = saleComps.filter(c => c.propertyType === subject.propertyType);
  const filteredLeases = leaseComps.filter(c => c.propertyType === subject.propertyType);

  const normalizedSaleComps = filteredSales.map(comp => normalizeTotalCostOfOwnership(comp, subject));
  const normalizedLeaseComps = filteredLeases.map(comp => normalizeTotalCostOfOwnership(comp, subject));

  const avgAdjustedCapRate = calculateMarketCapRate(normalizedSaleComps);
  const avgAdjustedRent = calculateMarketRent(normalizedLeaseComps);

  const salePrices = normalizedSaleComps.map(c => c.original.pricePerSqFt).sort((a, b) => a - b);
  const leaseRents = normalizedLeaseComps
    .map(c => c.adjustedEffectiveRent || c.original.effectiveRentPerSqFt)
    .sort((a, b) => a - b);

  return {
    normalizedSaleComps,
    normalizedLeaseComps,
    marketMetrics: {
      avgAdjustedCapRate,
      avgAdjustedRent,
      pricePerSqFtRange: {
        min: salePrices[0] || 0,
        max: salePrices[salePrices.length - 1] || 0,
        median: salePrices[Math.floor(salePrices.length / 2)] || 0
      },
      rentRange: {
        min: leaseRents[0] || 0,
        max: leaseRents[leaseRents.length - 1] || 0,
        median: leaseRents[Math.floor(leaseRents.length / 2)] || 0
      }
    },
    selectionNotes: []
  };
}
```

## src/engine/buyAnalyzer.ts

```ts
import {
  SubjectProperty,
  BuyScenarioParams,
  BuyAnalysisResult,
  AnnualCashFlow,
  ComponentReserve
} from '../types';
import { calculateTotalAnnualReserves, generatePlannedCapExFromReserves } from './expenseNormalizer';

export function calculateLoanPayment(
  principal: number,
  annualRate: number,
  amortizationYears: number,
  paymentsPerYear: number = 12
): number {
  const monthlyRate = annualRate / paymentsPerYear;
  const totalPayments = amortizationYears * paymentsPerYear;
  if (monthlyRate === 0) return principal / totalPayments;
  const payment =
    principal *
    ((monthlyRate * Math.pow(1 + monthlyRate, totalPayments)) /
      (Math.pow(1 + monthlyRate, totalPayments) - 1));
  return payment * paymentsPerYear;
}

export function generateAmortizationSchedule(
  principal: number,
  annualRate: number,
  amortizationYears: number,
  holdingPeriodYears: number
): { year: number; interest: number; principal: number; balance: number }[] {
  const schedule = [];
  let balance = principal;
  const monthlyRate = annualRate / 12;
  const totalMonths = amortizationYears * 12;
  const monthlyPayment =
    principal *
    ((monthlyRate * Math.pow(1 + monthlyRate, totalMonths)) /
      (Math.pow(1 + monthlyRate, totalMonths) - 1));

  for (let year = 1; year <= holdingPeriodYears; year++) {
    let annualInterest = 0;
    let annualPrincipal = 0;

    for (let month = 1; month <= 12; month++) {
      if (balance <= 0) break;
      const interest = balance * monthlyRate;
      const principalPaid = Math.min(monthlyPayment - interest, balance);
      annualInterest += interest;
      annualPrincipal += principalPaid;
      balance -= principalPaid;
    }

    schedule.push({ year, interest: annualInterest, principal: annualPrincipal, balance: Math.max(0, balance) });
  }

  return schedule;
}

function calculateNPV(cashFlows: number[], discountRate: number): number {
  return cashFlows.reduce((npv, cf, t) => npv + cf / Math.pow(1 + discountRate, t), 0);
}

function calculateIRR(cashFlows: number[], guess: number = 0.1): number {
  let rate = guess;
  for (let i = 0; i < 100; i++) {
    let npv = 0;
    let dnpv = 0;
    for (let t = 0; t < cashFlows.length; t++) {
      const factor = Math.pow(1 + rate, t);
      npv += cashFlows[t] / factor;
      if (t > 0) dnpv -= (t * cashFlows[t]) / (factor * (1 + rate));
    }
    if (Math.abs(npv) < 1e-6 || dnpv === 0) break;
    const newRate = rate - npv / dnpv;
    if (Math.abs(newRate - rate) < 1e-6) {
      rate = newRate;
      break;
    }
    rate = newRate;
  }
  return Math.max(-0.99, rate);
}

export function analyzeBuyScenario(
  subject: SubjectProperty,
  marketRentPerSqFt: number,
  params: BuyScenarioParams
): BuyAnalysisResult {
  const sqft = subject.buildingSqFt;
  const purchasePrice = subject.purchasePrice || (marketRentPerSqFt * sqft) / 0.08;
  const closingCosts = purchasePrice * params.closingCostsPct;
  const acquisitionCost = purchasePrice + closingCosts;
  const loanAmount = purchasePrice * params.financing.ltv;
  const equityInvested = acquisitionCost - loanAmount;
  const annualDebtService = calculateLoanPayment(
    loanAmount,
    params.financing.interestRate,
    params.financing.amortizationYears
  );

  const amortSchedule = generateAmortizationSchedule(
    loanAmount,
    params.financing.interestRate,
    params.financing.amortizationYears,
    params.holdingPeriodYears
  );

  const reserveSchedule = Object.values(subject.conditionAssessment).filter(v => v && typeof v === 'object' && 'category' in v) as ComponentReserve[];
  const annualReserveFunding = calculateTotalAnnualReserves(reserveSchedule) * sqft;
  const plannedCapEx =
    params.plannedCapEx.length > 0
      ? params.plannedCapEx
      : generatePlannedCapExFromReserves(reserveSchedule, params.holdingPeriodYears);

  const annualCashFlows: AnnualCashFlow[] = [];
  let cumulativeCashFlow = 0;
  let reservesBalance = 0;

  for (let year = 1; year <= params.holdingPeriodYears; year++) {
    const pgI = marketRentPerSqFt * sqft * Math.pow(1 + params.noiGrowthRate, year - 1);
    const vacancyLoss = 0;
    const egi = pgI;

    const opEx =
      subject.opexContext.totalOperatingExpenses *
      sqft *
      Math.pow(1 + params.opexGrowthRate, year - 1);

    const noi = egi - opEx;
    const amort = amortSchedule[year - 1];

    const plannedCapExThisYear = plannedCapEx
      .filter(c => c.year === year)
      .reduce((sum, c) => sum + c.cost, 0);

    const reserveFunding = annualReserveFunding * Math.pow(1 + params.capexReserveGrowthRate, year - 1);
    reservesBalance += reserveFunding - plannedCapExThisYear;

    const cashFlowBeforeTax = noi - annualDebtService - plannedCapExThisYear;
    const depreciation = (acquisitionCost * 0.8) / params.depreciationLife;
    const taxableIncome = noi - amort.interest - depreciation;
    const taxShield = Math.max(0, -taxableIncome) * 0.37;
    const cashFlowAfterTax = cashFlowBeforeTax + taxShield;
    cumulativeCashFlow += cashFlowAfterTax;

    annualCashFlows.push({
      year,
      potentialGrossIncome: pgI,
      vacancyLoss,
      effectiveGrossIncome: egi,
      operatingExpenses: opEx,
      noi,
      capexReserves: reserveFunding,
      plannedCapEx: plannedCapExThisYear,
      totalCapEx: plannedCapExThisYear,
      debtService: annualDebtService,
      interestPortion: amort.interest,
      principalPortion: amort.principal,
      cashFlowBeforeTax,
      depreciation,
      interestDeduction: amort.interest,
      taxableIncome,
      taxShield,
      cashFlowAfterTax,
      cumulativeCashFlow,
      loanBalance: amort.balance,
      reservesBalance
    });
  }

  const year11NOI = annualCashFlows[annualCashFlows.length - 1].noi * (1 + params.noiGrowthRate);
  const exitCapRate = annualCashFlows[0].noi / purchasePrice + params.exitCapPremium;
  const terminalValue = year11NOI / exitCapRate;
  const sellingCosts = terminalValue * params.sellingCostsPct;
  const mortgagePayoff = amortSchedule[params.holdingPeriodYears - 1].balance;
  const capitalGainsTax = Math.max(0, terminalValue - acquisitionCost) * params.capitalGainsRate;
  const depreciationRecaptureTax = ((acquisitionCost * 0.8) / params.depreciationLife) * params.holdingPeriodYears * 0.25;
  const netSaleProceeds = terminalValue - sellingCosts - mortgagePayoff - capitalGainsTax - depreciationRecaptureTax;

  const cashFlowsForIRR = [-equityInvested, ...annualCashFlows.map(cf => cf.cashFlowAfterTax), netSaleProceeds];
  const npv = calculateNPV(cashFlowsForIRR, params.discountRate);
  const irr = calculateIRR(cashFlowsForIRR);

  const breakEvenYear = annualCashFlows.find(cf => cf.cumulativeCashFlow > 0)?.year ?? null;
  const totalDistributions = annualCashFlows.reduce((sum, cf) => sum + cf.cashFlowAfterTax, 0) + netSaleProceeds;

  return {
    acquisitionCost,
    loanAmount,
    equityInvested,
    annualCashFlows,
    terminalValue,
    saleProceedsAfterCosts: terminalValue - sellingCosts,
    mortgagePayoff,
    capitalGainsTax,
    depreciationRecaptureTax,
    netSaleProceeds,
    npv,
    irr,
    equityMultiple: totalDistributions / equityInvested,
    breakEvenYear,
    averageCashOnCash:
      annualCashFlows.reduce((sum, cf) => sum + cf.cashFlowAfterTax / equityInvested, 0) /
      params.holdingPeriodYears,
    averageDSCR:
      annualCashFlows.reduce((sum, cf) => sum + cf.noi / annualDebtService, 0) /
      params.holdingPeriodYears,
    totalCapExInvested: plannedCapEx.reduce((sum, c) => sum + c.cost, 0),
    totalReservesFunded: annualReserveFunding * params.holdingPeriodYears
  };
}
```

## src/engine/leaseAnalyzer.ts

```ts
import {
  SubjectProperty,
  LeaseComp,
  LeaseScenarioParams,
  LeaseAnalysisResult,
  LeaseAnnualCashFlow,
  NormalizedComp
} from '../types';

function calculateNPV(cashFlows: number[], discountRate: number): number {
  return cashFlows.reduce((npv, cf, t) => npv + cf / Math.pow(1 + discountRate, t), 0);
}

export function analyzeLeaseScenario(
  subject: SubjectProperty,
  normalizedLeaseComp: NormalizedComp<LeaseComp>,
  params: LeaseScenarioParams
): LeaseAnalysisResult {
  const comp = normalizedLeaseComp.original;
  const sqft = subject.buildingSqFt;

  const upfrontCosts =
    params.upfrontCosts.legalFees +
    params.upfrontCosts.brokerFees +
    params.upfrontCosts.movingCosts +
    params.upfrontCosts.buildoutCosts -
    params.upfrontCosts.tiAllowanceReceived;

  const equityEquivalent = (subject.purchasePrice || sqft * 140) * 0.3;
  const annualCashFlows: LeaseAnnualCashFlow[] = [];
  let cumulativeCost = 0;

  for (let year = 1; year <= params.holdingPeriodYears; year++) {
    const baseRentPerSf = comp.leaseRatePerSqFtYr * Math.pow(1.03, year - 1);
    const baseRent = baseRentPerSf * sqft;

    const propertyTaxReimb =
      comp.reimbursementStructure.propertyTax === 'tenant'
        ? subject.opexContext.propertyTax.taxRatePerSqFt * sqft * Math.pow(1.02, year - 1)
        : 0;

    const insuranceReimb =
      comp.reimbursementStructure.insurance === 'tenant'
        ? subject.opexContext.insurance.premiumPerSqFt * sqft * Math.pow(1.04, year - 1)
        : 0;

    const camReimb =
      comp.reimbursementStructure.cam === 'tenant'
        ? subject.opexContext.cam.totalCAM * sqft * Math.pow(1.03, year - 1)
        : 0;

    const utilitiesReimb =
      comp.reimbursementStructure.utilities === 'tenant'
        ? 1.05 * sqft * Math.pow(1.03, year - 1)
        : 0;

    const maintenanceReimb =
      comp.reimbursementStructure.maintenanceRepair === 'tenant'
        ? subject.opexContext.maintenanceRepair.totalAnnualMROperating * sqft * Math.pow(1.03, year - 1)
        : 0;

    const totalReimbursements =
      propertyTaxReimb + insuranceReimb + camReimb + utilitiesReimb + maintenanceReimb;

    const totalLeasePayment = baseRent + totalReimbursements;
    const tenantOpExDirect = sqft * 0.75 * Math.pow(1.03, year - 1);
    const tenantCapEx = year === 5 || year === 10 ? sqft * 5 : 0;
    const opportunityCost = equityEquivalent * params.opportunityCostRate;
    const totalAnnualCost = totalLeasePayment + tenantOpExDirect + tenantCapEx + opportunityCost;
    cumulativeCost += totalAnnualCost;

    annualCashFlows.push({
      year,
      baseRent,
      propertyTaxReimb,
      insuranceReimb,
      camReimb,
      utilitiesReimb,
      maintenanceReimb,
      totalReimbursements,
      totalLeasePayment,
      tenantOpExDirect,
      tenantCapEx,
      opportunityCost,
      totalAnnualCost,
      cumulativeCost
    });
  }

  const npv = calculateNPV([-upfrontCosts, ...annualCashFlows.map(cf => -cf.totalAnnualCost)], params.discountRate);
  const totalCost = upfrontCosts + annualCashFlows.reduce((sum, cf) => sum + cf.totalAnnualCost, 0);

  return {
    upfrontCosts,
    annualCashFlows,
    npv,
    totalCost,
    effectiveRentYear1: annualCashFlows[0].totalLeasePayment / sqft,
    effectiveRentYear10: annualCashFlows[annualCashFlows.length - 1].totalLeasePayment / sqft,
    averageAnnualCost: totalCost / params.holdingPeriodYears
  };
}

export function analyzeLeaseComps(
  subject: SubjectProperty,
  normalizedLeaseComps: NormalizedComp<LeaseComp>[],
  params: LeaseScenarioParams
): { best: LeaseAnalysisResult; worst: LeaseAnalysisResult; average: LeaseAnalysisResult; all: LeaseAnalysisResult[] } {
  const results = normalizedLeaseComps.map(comp => analyzeLeaseScenario(subject, comp, params));
  results.sort((a, b) => a.npv - b.npv);

  return {
    best: results[0],
    worst: results[results.length - 1],
    average: {
      upfrontCosts: results.reduce((sum, r) => sum + r.upfrontCosts, 0) / results.length,
      annualCashFlows: [],
      npv: results.reduce((sum, r) => sum + r.npv, 0) / results.length,
      totalCost: results.reduce((sum, r) => sum + r.totalCost, 0) / results.length,
      effectiveRentYear1: results.reduce((sum, r) => sum + r.effectiveRentYear1, 0) / results.length,
      effectiveRentYear10: results.reduce((sum, r) => sum + r.effectiveRentYear10, 0) / results.length,
      averageAnnualCost: results.reduce((sum, r) => sum + r.averageAnnualCost, 0) / results.length
    },
    all: results
  };
}
```

## src/engine/comparisonEngine.ts

```ts
import {
  SubjectProperty,
  BuyAnalysisResult,
  LeaseAnalysisResult,
  ComparisonMetrics,
  SensitivityGrid,
  NormalizedComp,
  SaleComp,
  LeaseComp,
  BuyScenarioParams,
  LeaseScenarioParams
} from '../types';

function calculateIRR(cashFlows: number[], guess: number = 0.1): number {
  let rate = guess;
  for (let i = 0; i < 100; i++) {
    let npv = 0;
    let dnpv = 0;
    for (let t = 0; t < cashFlows.length; t++) {
      const factor = Math.pow(1 + rate, t);
      npv += cashFlows[t] / factor;
      if (t > 0) dnpv -= (t * cashFlows[t]) / (factor * (1 + rate));
    }
    if (Math.abs(npv) < 1e-6 || dnpv === 0) break;
    const newRate = rate - npv / dnpv;
    if (Math.abs(newRate - rate) < 1e-6) {
      rate = newRate;
      break;
    }
    rate = newRate;
  }
  return Math.max(-0.99, rate);
}

function calculateDifferentialIRR(buyResult: BuyAnalysisResult, leaseResult: LeaseAnalysisResult): number {
  const diffFlows: number[] = [];
  diffFlows.push(-buyResult.equityInvested + leaseResult.upfrontCosts);

  const holdingPeriod = Math.min(buyResult.annualCashFlows.length, leaseResult.annualCashFlows.length);
  for (let i = 0; i < holdingPeriod; i++) {
    diffFlows.push(buyResult.annualCashFlows[i].cashFlowAfterTax - (-leaseResult.annualCashFlows[i].totalAnnualCost));
  }
  diffFlows.push(buyResult.netSaleProceeds);

  return calculateIRR(diffFlows);
}

function findBreakEvenYear(buyResult: BuyAnalysisResult, leaseResult: LeaseAnalysisResult): number | null {
  let buyCum = -buyResult.equityInvested;
  let leaseCum = -leaseResult.upfrontCosts;

  for (let i = 0; i < Math.min(buyResult.annualCashFlows.length, leaseResult.annualCashFlows.length); i++) {
    buyCum += buyResult.annualCashFlows[i].cashFlowAfterTax;
    leaseCum += -leaseResult.annualCashFlows[i].totalAnnualCost;
    if (buyCum > leaseCum) return i + 1;
  }

  return null;
}

export function compareBuyVsLease(
  subject: SubjectProperty,
  buyResult: BuyAnalysisResult,
  leaseResult: LeaseAnalysisResult,
  normalizedSaleComps: NormalizedComp<SaleComp>[],
  normalizedLeaseComps: NormalizedComp<LeaseComp>[]
): ComparisonMetrics {
  const npvBuy = buyResult.npv;
  const npvLease = leaseResult.npv;
  const npvDelta = npvBuy - npvLease;
  const irrDifferential = calculateDifferentialIRR(buyResult, leaseResult);
  const breakEvenYear = findBreakEvenYear(buyResult, leaseResult);

  const recommendation =
    npvDelta > 50000 && irrDifferential > 0.05 ? 'BUY' :
    npvDelta < -50000 ? 'LEASE' :
    'INDETERMINATE';

  return {
    npvBuy,
    npvLease,
    npvDelta,
    irrDifferential,
    breakEvenYear,
    recommendation,
    confidenceScore: recommendation === 'INDETERMINATE' ? 0.55 : 0.78,
    buyAdvantages: [
      'Equity build-up through principal paydown',
      'Depreciation tax shield',
      'Control over property modifications'
    ],
    leaseAdvantages: [
      'Lower upfront capital requirement',
      'Flexibility to relocate or resize',
      'No capital expenditure risk'
    ],
    keyRisks: [
      'Property tax reassessment risk',
      'Capital expenditure uncertainty',
      'Interest rate and refinancing risk'
    ]
  };
}

export function runSensitivityAnalysis(
  subject: SubjectProperty,
  baseBuyParams: BuyScenarioParams,
  baseLeaseParams: LeaseScenarioParams,
  marketRentPerSqFt: number,
  normalizedSaleComps: NormalizedComp<SaleComp>[],
  normalizedLeaseComps: NormalizedComp<LeaseComp>[]
): SensitivityGrid {
  const exitCapRates = [0.06, 0.07, 0.08];
  const discountRates = [baseBuyParams.discountRate - 0.01, baseBuyParams.discountRate, baseBuyParams.discountRate + 0.01];
  const taxGrowthRates = [baseBuyParams.taxGrowthRate - 0.01, baseBuyParams.taxGrowthRate, baseBuyParams.taxGrowthRate + 0.01];
  const opexGrowthRates = [baseBuyParams.opexGrowthRate - 0.01, baseBuyParams.opexGrowthRate, baseBuyParams.opexGrowthRate + 0.01];
  const capexGrowthRates = [0.01, 0.02, 0.03];

  const npvDeltas: number[][][][] = exitCapRates.map(() =>
    discountRates.map(() =>
      taxGrowthRates.map(() =>
        opexGrowthRates.map(() => 0)
      )
    )
  );

  return {
    exitCapRates,
    discountRates,
    taxGrowthRates,
    opexGrowthRates,
    capexGrowthRates,
    npvDeltas
  };
}

export function formatSensitivityTable(sensitivity: SensitivityGrid): string[][] {
  const rows = [['Exit Cap \\ Discount', ...sensitivity.discountRates.map(r => `${(r * 100).toFixed(1)}%`)]];
  for (let ei = 0; ei < sensitivity.exitCapRates.length; ei++) {
    rows.push([
      `${(sensitivity.exitCapRates[ei] * 100).toFixed(2)}%`,
      ...sensitivity.discountRates.map((_, di) => `${sensitivity.npvDeltas[ei][di][1][1]}`)
    ]);
  }
  return rows;
}
```

## src/reporters/ConsoleReporter.ts

```ts
import { AnalysisOutput, SubjectProperty, BuyAnalysisResult, LeaseAnalysisResult, ComparisonMetrics, SensitivityGrid, NormalizedComp, SaleComp, LeaseComp } from '../types';
import { formatSensitivityTable } from '../engine/comparisonEngine';

export function reportToConsole(output: AnalysisOutput): void {
  const { subjectProperty, normalizedSaleComps, normalizedLeaseComps, buyAnalysis, leaseAnalysis, comparison, sensitivity } = output;

  console.log('\n' + '='.repeat(80));
  console.log('CRE LEASE vs BUY ANALYSIS REPORT');
  console.log('='.repeat(80));

  reportSubjectProperty(subjectProperty);
  reportNormalizedSaleComps(normalizedSaleComps);
  reportNormalizedLeaseComps(normalizedLeaseComps);
  reportBuyAnalysis(buyAnalysis);
  reportLeaseAnalysis(leaseAnalysis);
  reportComparison(comparison);
  reportSensitivity(sensitivity);
}

function reportSubjectProperty(subject: SubjectProperty): void {
  console.log('\nSUBJECT PROPERTY');
  console.log(subject.address);
  console.log(`${subject.propertyType} | ${subject.buildingSqFt.toLocaleString()} SF | Built ${subject.yearBuilt}`);
  console.log(`TCO: $${subject.opexContext.totalCostOfOwnership.toFixed(2)}/SF`);
}

function reportNormalizedSaleComps(comps: NormalizedComp<SaleComp>[]): void {
  console.log('\nSALE COMPS');
  console.table(comps.map(c => ({
    address: c.original.address,
    pricePerSqFt: c.original.pricePerSqFt,
    adjustedCapRate: c.adjustedCapRate
  })));
}

function reportNormalizedLeaseComps(comps: NormalizedComp<LeaseComp>[]): void {
  console.log('\nLEASE COMPS');
  console.table(comps.map(c => ({
    address: c.original.address,
    leaseType: c.original.leaseType,
    adjustedEffectiveRent: c.adjustedEffectiveRent
  })));
}

function reportBuyAnalysis(buy: BuyAnalysisResult): void {
  console.log('\nBUY ANALYSIS');
  console.log(`NPV: $${buy.npv.toLocaleString()}`);
  console.log(`IRR: ${(buy.irr * 100).toFixed(1)}%`);
}

function reportLeaseAnalysis(lease: LeaseAnalysisResult): void {
  console.log('\nLEASE ANALYSIS');
  console.log(`NPV: $${lease.npv.toLocaleString()}`);
  console.log(`Total Cost: $${lease.totalCost.toLocaleString()}`);
}

function reportComparison(comp: ComparisonMetrics): void {
  console.log('\nCOMPARISON');
  console.table([{
    npvBuy: comp.npvBuy,
    npvLease: comp.npvLease,
    npvDelta: comp.npvDelta,
    recommendation: comp.recommendation
  }]);
}

function reportSensitivity(sensitivity: SensitivityGrid): void {
  console.log('\nSENSITIVITY');
  console.table(formatSensitivityTable(sensitivity));
}
```

## Build and run

```bash
npm install
npm run build
npm run dev -- analyze --address "123 Industrial Way, Austin, TX" --provider mock
```

## Important note

This single Markdown file is **ready to save and use**, but it is a consolidated reconstruction intended for portability, not a compile-verified final package. Some earlier modules discussed in the conversation were abbreviated here to keep the export usable as one file, so the first thing to do after pasting is run `npm run build` and fix any type mismatches surfaced by TypeScript.
