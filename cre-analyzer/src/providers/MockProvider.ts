/**
 * Local fixture provider — runs instantly with zero credentials so CI and
 * `--provider mock` always work.
 *
 * Scenario: a 20,000 SF industrial building (built 2005) currently taxed at
 * $1.50/SF. On purchase it reassesses to ~$2.00/SF. Four sale comps and four
 * lease comps span a range of ages, sizes, tax bases and lease structures so
 * the normalization engine has something real to chew on:
 *   - one sale comp sold recently (high, reassessed tax basis)
 *   - one sale comp is old (stale, low tax basis)
 *   - leases: 2 x NNN, 1 x Modified Gross (expense stop), 1 x Gross
 */
import { IListingProvider, ListingBundle, ProviderContext } from './IListingProvider';
import {
  LeaseComp,
  PropertyTaxContext,
  SaleComp,
  SubjectProperty,
} from '../types';

function tax(
  ratePerSqFt: number,
  sqft: number,
  opts: Partial<PropertyTaxContext> = {}
): PropertyTaxContext {
  const annual = Number((ratePerSqFt * sqft).toFixed(2));
  return {
    annualTaxAmount: annual,
    taxRatePerSqFt: ratePerSqFt,
    assessmentYear: opts.assessmentYear ?? 2022,
    reassessmentTrigger: opts.reassessmentTrigger ?? 'sale',
    reassessmentValueBasis: opts.reassessmentValueBasis ?? 'sale_price',
    estimatedPostTransactionTax: opts.estimatedPostTransactionTax ?? annual,
    millageRate: opts.millageRate,
    assessmentRatio: opts.assessmentRatio,
    annualAssessmentCap: opts.annualAssessmentCap,
  };
}

const SUBJECT: SubjectProperty = {
  address: '123 Industrial Way, Austin, TX',
  propertyType: 'industrial',
  buildingSqFt: 20000,
  landAcres: 1.4,
  yearBuilt: 2005,
  taxContext: tax(1.5, 20000, {
    estimatedPostTransactionTax: 40000, // ~$2.00/SF after reassessment
    millageRate: 0.0222,
    assessmentRatio: 1.0,
    annualAssessmentCap: 0.1, // TX caps don't apply to commercial; modeled generously
  }),
};

const SALE_COMPS: SaleComp[] = [
  {
    id: 'S1',
    address: '450 Logistics Pkwy, Austin, TX',
    propertyType: 'industrial',
    buildingSqFt: 18000,
    landAcres: 1.2,
    yearBuilt: 2008,
    salePrice: 3420000, // $190/SF
    saleDate: '2026-02-15',
    noi: 232560, // ~6.8% reported cap, post (reassessed) tax
    pricePerSqFt: 190,
    capRate: 0.068,
    taxContext: tax(1.8, 18000, { assessmentYear: 2026 }), // recently reassessed
  },
  {
    id: 'S2',
    address: '88 Old Mill Rd, Round Rock, TX',
    propertyType: 'industrial',
    buildingSqFt: 22000,
    landAcres: 1.6,
    yearBuilt: 2002,
    salePrice: 3740000, // $170/SF
    saleDate: '2025-11-01',
    noi: 269280, // ~7.2% reported cap
    pricePerSqFt: 170,
    capRate: 0.072,
    taxContext: tax(0.9, 22000, { assessmentYear: 2015 }), // stale, low tax basis
  },
  {
    id: 'S3',
    address: '1200 Commerce Center Dr, Austin, TX',
    propertyType: 'industrial',
    buildingSqFt: 25000,
    landAcres: 1.9,
    yearBuilt: 2010,
    salePrice: 5000000, // $200/SF
    saleDate: '2025-09-20',
    noi: 325000, // ~6.5% reported cap
    pricePerSqFt: 200,
    capRate: 0.065,
    taxContext: tax(1.6, 25000, { assessmentYear: 2023 }),
  },
  {
    id: 'S4',
    address: '77 Warehouse Ln, Pflugerville, TX',
    propertyType: 'industrial',
    buildingSqFt: 15000,
    landAcres: 1.0,
    yearBuilt: 2000,
    salePrice: 2400000, // $160/SF
    saleDate: '2025-12-10',
    noi: 180000, // ~7.5% reported cap
    pricePerSqFt: 160,
    capRate: 0.075,
    taxContext: tax(1.2, 15000, { assessmentYear: 2019 }),
  },
];

const LEASE_COMPS: LeaseComp[] = [
  {
    id: 'L1',
    address: '300 Distribution Blvd, Austin, TX',
    propertyType: 'industrial',
    buildingSqFt: 19000,
    landAcres: 1.3,
    yearBuilt: 2007,
    leaseRatePerSqFtYr: 9.5,
    leaseType: 'NNN',
    opExBreakdown: { propertyTax: 1.5, insurance: 0.4, cam: 0.6, totalOpEx: 2.5 },
    effectiveRentPerSqFt: 12.0,
    leaseTermYears: 7,
    tenantImprovementAllowance: 5,
    freeRentMonths: 2,
    escalations: [{ type: 'fixed', rate: 0.03, startYear: 2 }],
    taxContext: tax(1.5, 19000),
  },
  {
    id: 'L2',
    address: '510 Freight St, Austin, TX',
    propertyType: 'industrial',
    buildingSqFt: 21000,
    landAcres: 1.5,
    yearBuilt: 2009,
    leaseRatePerSqFtYr: 10.0,
    leaseType: 'NNN',
    opExBreakdown: { propertyTax: 1.8, insurance: 0.5, cam: 0.7, totalOpEx: 3.0 },
    effectiveRentPerSqFt: 13.0,
    leaseTermYears: 10,
    tenantImprovementAllowance: 8,
    freeRentMonths: 3,
    escalations: [{ type: 'cpi', rate: 0.025, startYear: 2 }],
    taxContext: tax(1.8, 21000),
  },
  {
    id: 'L3',
    address: '215 Trade Center Ct, Round Rock, TX',
    propertyType: 'industrial',
    buildingSqFt: 17000,
    landAcres: 1.1,
    yearBuilt: 2004,
    leaseRatePerSqFtYr: 12.5,
    leaseType: 'Modified Gross',
    opExBreakdown: { propertyTax: 1.4, insurance: 0.45, cam: 0.65, totalOpEx: 2.5 },
    effectiveRentPerSqFt: 13.0,
    leaseTermYears: 5,
    tenantImprovementAllowance: 3,
    freeRentMonths: 1,
    escalations: [{ type: 'fixed', rate: 0.025, startYear: 2 }],
    expenseStopPerSqFt: 2.0, // tenant pays OpEx above $2.00/SF
    taxContext: tax(1.4, 17000),
  },
  {
    id: 'L4',
    address: '940 Gateway Industrial, Austin, TX',
    propertyType: 'industrial',
    buildingSqFt: 20000,
    landAcres: 1.4,
    yearBuilt: 2006,
    leaseRatePerSqFtYr: 13.5,
    leaseType: 'Gross',
    opExBreakdown: { propertyTax: 1.3, insurance: 0.4, cam: 0.6, totalOpEx: 2.3 },
    effectiveRentPerSqFt: 13.5,
    leaseTermYears: 7,
    tenantImprovementAllowance: 4,
    freeRentMonths: 2,
    escalations: [{ type: 'fixed', rate: 0.03, startYear: 2 }],
    taxContext: tax(1.3, 20000),
  },
];

export class MockProvider implements IListingProvider {
  readonly name = 'mock';
  readonly requiresCredentials = false;

  async fetchBundle(context: ProviderContext): Promise<ListingBundle> {
    const subject: SubjectProperty = {
      ...SUBJECT,
      // Honor a caller-supplied address while keeping the fixture attributes.
      address: context.address || SUBJECT.address,
    };
    return {
      subject,
      saleComps: SALE_COMPS.map((c) => ({ ...c })),
      leaseComps: LEASE_COMPS.map((c) => ({ ...c })),
    };
  }
}

/** Exported for tests and reuse. */
export const MOCK_SUBJECT = SUBJECT;
export const MOCK_SALE_COMPS = SALE_COMPS;
export const MOCK_LEASE_COMPS = LEASE_COMPS;
