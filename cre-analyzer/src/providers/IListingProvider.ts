/**
 * Adapter pattern for listing data sources.
 *
 * There is NO single API for "all commercial listings" — CoStar, Crexi,
 * LoopNet and the MLSs are walled gardens with five-figure annual price tags.
 * So we program against this interface and swap implementations: a local
 * MockProvider for CI, an interactive ManualEntryProvider for real workflows,
 * and credentialed adapters for the paid APIs.
 */
import { LeaseComp, SaleComp, SubjectProperty } from '../types';

export interface ProviderContext {
  /** Subject property address to anchor the comp search. */
  address: string;
  /** Optional desired comp count per type (defaults to 4). */
  compCount?: number;
}

export interface ListingBundle {
  subject: SubjectProperty;
  saleComps: SaleComp[];
  leaseComps: LeaseComp[];
}

export interface IListingProvider {
  /** Human-readable provider name. */
  readonly name: string;
  /** Whether the provider can run without external credentials. */
  readonly requiresCredentials: boolean;

  /** Resolve the subject property + comparable sales and leases. */
  fetchBundle(context: ProviderContext): Promise<ListingBundle>;
}
