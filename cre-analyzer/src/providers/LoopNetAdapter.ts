/**
 * LoopNet adapter (STUB). LoopNet (a CoStar property) is listings-focused;
 * sold-comp and tax data typically require the CoStar back-end. Treat this as a
 * thin marketplace source and enrich tax basis separately.
 *
 * Env vars expected: LOOPNET_API_KEY, LOOPNET_BASE_URL
 */
import { IListingProvider, ListingBundle, ProviderContext } from './IListingProvider';

export class LoopNetAdapter implements IListingProvider {
  readonly name = 'loopnet';
  readonly requiresCredentials = true;

  async fetchBundle(_context: ProviderContext): Promise<ListingBundle> {
    if (!process.env.LOOPNET_API_KEY) {
      throw new Error(
        'LoopNetAdapter requires LOOPNET_API_KEY. Use --provider mock for a credential-free run.'
      );
    }
    throw new Error('LoopNetAdapter is a stub. Implement the LoopNet listing mapping.');
  }
}
