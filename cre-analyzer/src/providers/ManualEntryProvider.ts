/**
 * Interactive manual-entry provider. Walks the user through the subject
 * property plus four sale comps and four lease comps with inline validation,
 * including the all-important "does this quote include property tax?" prompt
 * that the normalization engine depends on.
 */
import inquirer from 'inquirer';
import { IListingProvider, ListingBundle, ProviderContext } from './IListingProvider';
import {
  EscalationClause,
  LeaseComp,
  LeaseStructure,
  PropertyType,
  SaleComp,
  SubjectProperty,
} from '../types';

const PROPERTY_TYPES: PropertyType[] = [
  'office',
  'industrial',
  'retail',
  'multifamily',
  'land',
];

const LEASE_TYPES: LeaseStructure[] = [
  'NNN',
  'NN',
  'N',
  'Gross',
  'Modified Gross',
];

const requiredNumber = (input: string): true | string => {
  const n = Number(input);
  return Number.isFinite(n) && n >= 0 ? true : 'Enter a non-negative number.';
};

const requiredText = (input: string): true | string =>
  input.trim().length > 0 ? true : 'This field is required.';

type Answers = Record<string, any>;

async function promptSubject(defaultAddress: string): Promise<SubjectProperty> {
  const a: Answers = await inquirer.prompt([
    { name: 'address', message: 'Subject address:', default: defaultAddress, validate: requiredText },
    { name: 'propertyType', type: 'list', message: 'Property type:', choices: PROPERTY_TYPES },
    { name: 'buildingSqFt', message: 'Building SF:', validate: requiredNumber, filter: Number },
    { name: 'landAcres', message: 'Land acres:', default: '0', filter: Number },
    { name: 'yearBuilt', message: 'Year built:', validate: requiredNumber, filter: Number },
    { name: 'currentTaxRate', message: 'Current property tax ($/SF/yr):', validate: requiredNumber, filter: Number },
    {
      name: 'reassessmentTrigger',
      type: 'list',
      message: 'On purchase, does the assessment reset?',
      choices: ['sale', 'cycle', 'improvement', 'none'],
      default: 'sale',
    },
    { name: 'postSaleTaxRate', message: 'Projected post-purchase tax ($/SF/yr):', validate: requiredNumber, filter: Number },
  ]);

  return {
    address: a.address,
    propertyType: a.propertyType,
    buildingSqFt: a.buildingSqFt,
    landAcres: a.landAcres,
    yearBuilt: a.yearBuilt,
    taxContext: {
      annualTaxAmount: a.currentTaxRate * a.buildingSqFt,
      taxRatePerSqFt: a.currentTaxRate,
      assessmentYear: new Date().getFullYear(),
      reassessmentTrigger: a.reassessmentTrigger,
      reassessmentValueBasis: 'sale_price',
      estimatedPostTransactionTax: a.postSaleTaxRate * a.buildingSqFt,
    },
  };
}

async function promptSaleComp(i: number, type: PropertyType): Promise<SaleComp> {
  const a: Answers = await inquirer.prompt([
    { name: 'address', message: `Sale comp #${i} address:`, validate: requiredText },
    { name: 'buildingSqFt', message: 'Building SF:', validate: requiredNumber, filter: Number },
    { name: 'yearBuilt', message: 'Year built:', validate: requiredNumber, filter: Number },
    { name: 'salePrice', message: 'Sale price ($):', validate: requiredNumber, filter: Number },
    { name: 'saleDate', message: 'Sale date (YYYY-MM-DD):', default: '2025-01-01' },
    {
      name: 'noiIncludesTax',
      type: 'confirm',
      message: 'Does the reported NOI already DEDUCT property taxes?',
      default: true,
    },
    { name: 'noi', message: 'Net Operating Income ($/yr):', validate: requiredNumber, filter: Number },
    { name: 'taxRate', message: "Comp's property tax ($/SF/yr):", validate: requiredNumber, filter: Number },
  ]);

  // If NOI did NOT already deduct tax, deduct it now so NOI is post-tax (our contract).
  const annualTax = a.taxRate * a.buildingSqFt;
  const postTaxNoi = a.noiIncludesTax ? a.noi : a.noi - annualTax;

  return {
    id: `S${i}`,
    address: a.address,
    propertyType: type,
    buildingSqFt: a.buildingSqFt,
    landAcres: 0,
    yearBuilt: a.yearBuilt,
    salePrice: a.salePrice,
    saleDate: a.saleDate,
    noi: postTaxNoi,
    pricePerSqFt: a.salePrice / a.buildingSqFt,
    capRate: postTaxNoi / a.salePrice,
    taxContext: {
      annualTaxAmount: annualTax,
      taxRatePerSqFt: a.taxRate,
      assessmentYear: new Date().getFullYear() - 1,
      reassessmentTrigger: 'sale',
      reassessmentValueBasis: 'sale_price',
      estimatedPostTransactionTax: annualTax,
    },
  };
}

async function promptLeaseComp(i: number, type: PropertyType): Promise<LeaseComp> {
  const a: Answers = await inquirer.prompt([
    { name: 'address', message: `Lease comp #${i} address:`, validate: requiredText },
    { name: 'buildingSqFt', message: 'Building SF:', validate: requiredNumber, filter: Number },
    { name: 'yearBuilt', message: 'Year built:', validate: requiredNumber, filter: Number },
    { name: 'leaseType', type: 'list', message: 'Lease structure:', choices: LEASE_TYPES },
    { name: 'baseRent', message: 'Base rent ($/SF/yr):', validate: requiredNumber, filter: Number },
    {
      name: 'includesTax',
      type: 'confirm',
      message: 'Does this lease comp include property taxes (pass-through or embedded)?',
      default: true,
    },
    { name: 'tax', message: 'Property tax ($/SF/yr):', validate: requiredNumber, filter: Number },
    { name: 'insurance', message: 'Insurance ($/SF/yr):', default: '0', filter: Number },
    { name: 'cam', message: 'CAM ($/SF/yr):', default: '0', filter: Number },
    { name: 'leaseTermYears', message: 'Lease term (years):', default: '5', filter: Number },
    { name: 'tenantImprovementAllowance', message: 'TI allowance ($/SF):', default: '0', filter: Number },
    { name: 'freeRentMonths', message: 'Free rent (months):', default: '0', filter: Number },
    { name: 'escalationRate', message: 'Annual escalation (%):', default: '3', filter: Number },
    {
      name: 'expenseStop',
      message: 'Base-year expense stop ($/SF, blank if none):',
      default: '',
      when: (ans: Answers) => ans.leaseType === 'Modified Gross',
    },
  ]);

  const totalOpEx = a.tax + a.insurance + a.cam;
  const escalations: EscalationClause[] = [
    { type: 'fixed', rate: a.escalationRate / 100, startYear: 2 },
  ];

  return {
    id: `L${i}`,
    address: a.address,
    propertyType: type,
    buildingSqFt: a.buildingSqFt,
    landAcres: 0,
    yearBuilt: a.yearBuilt,
    leaseRatePerSqFtYr: a.baseRent,
    leaseType: a.leaseType,
    opExBreakdown: {
      propertyTax: a.tax,
      insurance: a.insurance,
      cam: a.cam,
      totalOpEx,
    },
    effectiveRentPerSqFt: a.baseRent + (a.leaseType === 'Gross' ? 0 : totalOpEx),
    leaseTermYears: a.leaseTermYears,
    tenantImprovementAllowance: a.tenantImprovementAllowance,
    freeRentMonths: a.freeRentMonths,
    escalations,
    expenseStopPerSqFt:
      a.expenseStop === '' || a.expenseStop == null ? undefined : Number(a.expenseStop),
    taxContext: {
      annualTaxAmount: a.tax * a.buildingSqFt,
      taxRatePerSqFt: a.tax,
      assessmentYear: new Date().getFullYear(),
      reassessmentTrigger: 'none',
      reassessmentValueBasis: 'assessed_value',
      estimatedPostTransactionTax: a.tax * a.buildingSqFt,
    },
  };
}

export class ManualEntryProvider implements IListingProvider {
  readonly name = 'manual';
  readonly requiresCredentials = false;

  constructor(private readonly compCount = 4) {}

  async fetchBundle(context: ProviderContext): Promise<ListingBundle> {
    const count = context.compCount ?? this.compCount;
    const subject = await promptSubject(context.address);

    const saleComps: SaleComp[] = [];
    for (let i = 1; i <= count; i++) {
      saleComps.push(await promptSaleComp(i, subject.propertyType));
    }

    const leaseComps: LeaseComp[] = [];
    for (let i = 1; i <= count; i++) {
      leaseComps.push(await promptLeaseComp(i, subject.propertyType));
    }

    return { subject, saleComps, leaseComps };
  }
}
