/**
 * Core data models for the CRE Lease vs. Buy analysis engine.
 *
 * CRITICAL CONVENTION: Every monetary field is **annualized** and, unless the
 * field name says otherwise, **tax-inclusive**. Property taxes are never an
 * afterthought here — they are a first-class part of every comp via
 * {@link PropertyTaxContext}.
 */

// ---------------------------------------------------------------------------
// Property tax
// ---------------------------------------------------------------------------

export type PropertyType =
  | 'office'
  | 'industrial'
  | 'retail'
  | 'multifamily'
  | 'land';

export type ReassessmentTrigger = 'sale' | 'improvement' | 'cycle' | 'none';

export type ReassessmentValueBasis =
  | 'sale_price'
  | 'market_value'
  | 'assessed_value';

/**
 * Everything required to understand and project a property's tax burden.
 *
 * `annualTaxAmount` is the *total* current tax bill in dollars.
 * `taxRatePerSqFt` is the derived $/SF/yr (annualTaxAmount / buildingSqFt).
 * `estimatedPostTransactionTax` is the *total* projected Year-1 bill **if the
 * property were purchased today** (i.e. after any sale-triggered reassessment).
 */
export interface PropertyTaxContext {
  /** Current annual tax bill in dollars (total, not per-SF). */
  annualTaxAmount: number;
  /** Derived $/SF/yr (annualTaxAmount / buildingSqFt). */
  taxRatePerSqFt: number;
  /** Year the current assessment was set. */
  assessmentYear: number;
  /** What causes the assessment to reset. */
  reassessmentTrigger: ReassessmentTrigger;
  /** What value the new assessment is keyed off of. */
  reassessmentValueBasis: ReassessmentValueBasis;
  /** Projected total annual tax in Year 1 IF the property is bought today. */
  estimatedPostTransactionTax: number;

  /** Optional jurisdiction parameters used to *derive* a post-sale tax. */
  millageRate?: number; // e.g. 0.025 means 2.5% of assessed value
  assessmentRatio?: number; // e.g. 1.0 (FL) or fractional ratios
  /** Annual statutory cap on assessed-value growth (e.g. 0.02 = Prop 13 / FL). */
  annualAssessmentCap?: number;
}

// ---------------------------------------------------------------------------
// Comps
// ---------------------------------------------------------------------------

export interface BaseComp {
  id: string;
  address: string;
  propertyType: PropertyType;
  buildingSqFt: number;
  landAcres: number;
  yearBuilt: number;
  /** MANDATORY — taxes are normalized off of this. */
  taxContext: PropertyTaxContext;
}

export interface SaleComp extends BaseComp {
  /** Total consideration ($). */
  salePrice: number;
  /** ISO date string. */
  saleDate: string;
  /** NOI / Price. NOI MUST be post-(property)tax. Optional / derivable. */
  capRate?: number;
  /** Net Operating Income AFTER property taxes ($, total annual). */
  noi: number;
  pricePerSqFt: number;
}

export type LeaseStructure = 'NNN' | 'NN' | 'N' | 'Gross' | 'Modified Gross';

export type EscalationType = 'fixed' | 'cpi' | 'porters';

export interface EscalationClause {
  type: EscalationType;
  /** Annual escalation rate (e.g. 0.03 for 3%). For CPI this is the assumed CPI. */
  rate: number;
  /** First lease year the escalation applies (1-based). Defaults to 2. */
  startYear?: number;
}

export interface OpExBreakdown {
  /** $/SF/yr — property tax component (reimbursed or landlord expense). */
  propertyTax: number;
  insurance: number;
  cam: number;
  /** $/SF/yr — total operating expenses. */
  totalOpEx: number;
}

export interface LeaseComp extends BaseComp {
  /** Base rent $/SF/yr. */
  leaseRatePerSqFtYr: number;
  leaseType: LeaseStructure;
  /** OpEx breakdown — must separate taxes. */
  opExBreakdown: OpExBreakdown;
  /** Base rent + tenant-paid OpEx (incl. tax), $/SF/yr. */
  effectiveRentPerSqFt: number;
  leaseTermYears: number;
  /** $/SF tenant-improvement allowance. */
  tenantImprovementAllowance: number;
  freeRentMonths: number;
  escalations: EscalationClause[];
  /**
   * For Modified Gross / base-year leases: the expense level (in $/SF) frozen
   * into the base year. Tenant pays only increases over this stop.
   */
  expenseStopPerSqFt?: number;
}

// ---------------------------------------------------------------------------
// Subject property
// ---------------------------------------------------------------------------

/**
 * The property under analysis. We never have it simultaneously listed for both
 * sale and lease — instead we derive its value from comps normalized to its
 * own tax context (see compSelector).
 */
export interface SubjectProperty {
  address: string;
  propertyType: PropertyType;
  buildingSqFt: number;
  landAcres: number;
  yearBuilt: number;
  taxContext: PropertyTaxContext;
}

// ---------------------------------------------------------------------------
// Normalized comps (output of the tax normalizer)
// ---------------------------------------------------------------------------

export interface NormalizedSaleComp {
  comp: SaleComp;
  /** Reported (post-old-tax) NOI. */
  reportedNoi: number;
  /** The comp's own annual tax that was baked into the reported NOI ($). */
  oldAnnualTax: number;
  /** Subject's projected annual tax applied to this comp's SF ($). */
  newProjectedTax: number;
  /** NOI restated under the subject's tax burden ($). */
  adjustedNoi: number;
  /** adjustedNoi / salePrice. */
  adjustedCapRate: number;
  /** Reported cap rate (reportedNoi / salePrice). */
  reportedCapRate: number;
  pricePerSqFt: number;
}

export interface NormalizedLeaseComp {
  comp: LeaseComp;
  /** All-in NNN-equivalent occupancy cost at the comp's own tax ($/SF/yr). */
  nnnEquivalentRent: number;
  /** All-in occupancy cost restated at the subject's projected tax ($/SF/yr). */
  subjectAdjustedRent: number;
  /** The comp's property-tax component used in the restatement ($/SF/yr). */
  compTaxPerSqFt: number;
  /** Subject's projected property-tax component ($/SF/yr). */
  subjectTaxPerSqFt: number;
}

/** Discriminated union returned by the generic normalizeTaxes() entry point. */
export type NormalizedComp =
  | ({ kind: 'sale' } & NormalizedSaleComp)
  | ({ kind: 'lease' } & NormalizedLeaseComp);

// ---------------------------------------------------------------------------
// Market derivation (compSelector output)
// ---------------------------------------------------------------------------

export interface MarketDerivation {
  normalizedSales: NormalizedSaleComp[];
  normalizedLeases: NormalizedLeaseComp[];
  /** Average tax-adjusted $/SF from sale comps. */
  avgAdjustedPricePerSqFt: number;
  /** Average tax-adjusted cap rate from sale comps. */
  avgAdjustedCapRate: number;
  /** Average all-in market rent ($/SF/yr) at the subject's tax. */
  avgSubjectAdjustedRent: number;
  /** Average non-tax OpEx (insurance + CAM), $/SF/yr, from lease comps. */
  avgNonTaxOpExPerSqFt: number;
  /** Derived total purchase price for the subject. */
  derivedPurchasePrice: number;
}

// ---------------------------------------------------------------------------
// Analysis inputs / outputs
// ---------------------------------------------------------------------------

export interface AnalysisAssumptions {
  holdingPeriodYears: number;
  discountRate: number; // WACC / cost of capital
  ltv: number; // 0..1
  interestRate: number;
  amortizationYears: number;
  closingCostPct: number; // default 0.025
  exitCapPremium: number; // bps over entry cap, e.g. 0.0075
  sellingCostPct: number; // default 0.05
  rentGrowthRate: number; // annual market rent growth
  taxGrowthRate: number; // annual property tax growth
  reservesPerSqFt: number; // default 0.15
  managementFeePct: number; // default 0.03
  marginalTaxRate: number; // for depreciation/interest shield
  capitalGainsRate: number; // on appreciation at sale
  depreciationRecaptureRate: number; // on accumulated depreciation
  buildingValuePct: number; // portion of price that is depreciable improvements
  depreciationLifeYears: number; // 39 commercial / 27.5 residential
  // Lease-side upfront costs
  leaseLegalBrokerPerSqFt: number;
  movingCostPerSqFt: number;
  /** Annual return on equity that is NOT spent buying (opportunity cost). */
  opportunityCostRate: number;
}

export interface YearlyBuyCashFlow {
  year: number;
  noi: number;
  debtService: number;
  interestPortion: number;
  principalPortion: number;
  depreciation: number;
  taxShield: number;
  propertyTax: number;
  /** Pre-tax-shield operating cash flow (NOI - debt service). */
  operatingCashFlow: number;
  /** Including tax shield and (year N) net sale proceeds. */
  netCashFlow: number;
  loanBalanceEnd: number;
}

export interface BuyAnalysis {
  purchasePrice: number;
  closingCosts: number;
  loanAmount: number;
  equity: number;
  annualDebtService: number;
  entryCapRate: number;
  exitCapRate: number;
  terminalValue: number;
  netSaleProceeds: number;
  cashFlows: YearlyBuyCashFlow[];
  /** Full investment cash-flow vector incl. year-0 equity outflow. */
  investmentCashFlowVector: number[];
  irr: number;
  npv: number;
  /** Annual all-in cost of ownership by year (for differential analysis). */
  annualOwnershipCost: number[];
  upfrontCost: number;
}

export interface YearlyLeaseCashFlow {
  year: number;
  baseRent: number;
  opExReimbursement: number;
  freeRentCredit: number;
  /** Total annual lease payment ($). */
  leasePayment: number;
  /** Opportunity gain on invested equity that buying would have consumed. */
  opportunityGain: number;
}

export interface LeaseAnalysis {
  marketRentPerSqFt: number;
  upfrontCost: number;
  tiOffset: number;
  cashFlows: YearlyLeaseCashFlow[];
  /** Total cost cash-flow vector (negative outflows). */
  costCashFlowVector: number[];
  npvCost: number;
  annualLeaseCost: number[];
}

export interface ComparisonResult {
  buy: BuyAnalysis;
  lease: LeaseAnalysis;
  buyNpvCost: number;
  leaseNpvCost: number;
  npvAdvantageOfBuying: number; // leaseNpvCost - buyNpvCost; positive => buy wins
  differentialIrr: number;
  breakEvenYear: number | null;
  recommendation: 'BUY' | 'LEASE' | 'TOSS_UP';
  rationale: string;
}

export interface SensitivityCell {
  exitCapRate: number;
  discountRate: number;
  taxGrowthRate: number;
  npvAdvantageOfBuying: number;
}

export interface SensitivityTable {
  taxGrowthRate: number;
  exitCapRates: number[];
  discountRates: number[];
  cells: SensitivityCell[];
}

export interface AnalysisResult {
  subject: SubjectProperty;
  assumptions: AnalysisAssumptions;
  market: MarketDerivation;
  comparison: ComparisonResult;
  sensitivity: SensitivityTable[];
  generatedAt: string;
}
