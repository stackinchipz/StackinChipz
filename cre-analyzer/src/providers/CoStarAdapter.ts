/**
 * CoStar adapter (STUB).
 *
 * CoStar is the gold-standard CRE data platform but access is enterprise-only
 * ($$$$/yr) and gated behind credentials + a negotiated API contract. This stub
 * documents the integration shape; wire in the real HTTP calls once you have
 * keys.
 *
 * Env vars expected:
 *   COSTAR_API_KEY, COSTAR_API_SECRET, COSTAR_BASE_URL
 */
import { IListingProvider, ListingBundle, ProviderContext } from './IListingProvider';

export interface CoStarCredentials {
  apiKey: string;
  apiSecret: string;
  baseUrl?: string;
}

export class CoStarAdapter implements IListingProvider {
  readonly name = 'costar';
  readonly requiresCredentials = true;

  constructor(private readonly creds?: CoStarCredentials) {}

  private resolveCreds(): CoStarCredentials {
    const apiKey = this.creds?.apiKey ?? process.env.COSTAR_API_KEY;
    const apiSecret = this.creds?.apiSecret ?? process.env.COSTAR_API_SECRET;
    if (!apiKey || !apiSecret) {
      throw new Error(
        'CoStarAdapter requires COSTAR_API_KEY and COSTAR_API_SECRET. ' +
          'See README "API Key setup". Use --provider mock for a credential-free run.'
      );
    }
    return {
      apiKey,
      apiSecret,
      baseUrl: this.creds?.baseUrl ?? process.env.COSTAR_BASE_URL,
    };
  }

  async fetchBundle(_context: ProviderContext): Promise<ListingBundle> {
    this.resolveCreds();
    // TODO: 1) geocode subject address, 2) GET /properties/{id} for attributes
    //       + tax history, 3) GET /comps/sales and /comps/leases filtered by
    //       type/size/radius, 4) map the CoStar schema onto our types, taking
    //       care to capture each comp's tax basis for normalization.
    throw new Error(
      'CoStarAdapter is a stub. Implement the CoStar REST mapping, then remove this throw.'
    );
  }
}
