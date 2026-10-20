/**
 * Crexi adapter (STUB). Crexi exposes marketplace listings; tax history is
 * thinner than CoStar, so plan to enrich with a county assessor / ATTOM lookup
 * for the normalization step.
 *
 * Env vars expected: CREXI_API_KEY, CREXI_BASE_URL
 */
import { IListingProvider, ListingBundle, ProviderContext } from './IListingProvider';

export class CrexiAdapter implements IListingProvider {
  readonly name = 'crexi';
  readonly requiresCredentials = true;

  async fetchBundle(_context: ProviderContext): Promise<ListingBundle> {
    if (!process.env.CREXI_API_KEY) {
      throw new Error(
        'CrexiAdapter requires CREXI_API_KEY. Use --provider mock for a credential-free run.'
      );
    }
    throw new Error('CrexiAdapter is a stub. Implement the Crexi listing mapping.');
  }
}
