/** Provider registry / factory keyed by the `--provider` CLI flag. */
import { IListingProvider } from './IListingProvider';
import { MockProvider } from './MockProvider';
import { ManualEntryProvider } from './ManualEntryProvider';
import { CoStarAdapter } from './CoStarAdapter';
import { CrexiAdapter } from './CrexiAdapter';
import { LoopNetAdapter } from './LoopNetAdapter';

export type ProviderName = 'mock' | 'manual' | 'costar' | 'crexi' | 'loopnet';

export function createProvider(name: string): IListingProvider {
  switch (name as ProviderName) {
    case 'mock':
      return new MockProvider();
    case 'manual':
      return new ManualEntryProvider();
    case 'costar':
      return new CoStarAdapter();
    case 'crexi':
      return new CrexiAdapter();
    case 'loopnet':
      return new LoopNetAdapter();
    default:
      throw new Error(
        `Unknown provider "${name}". Choose: mock, manual, costar, crexi, loopnet.`
      );
  }
}

export * from './IListingProvider';
export { MockProvider } from './MockProvider';
export { ManualEntryProvider } from './ManualEntryProvider';
export { CoStarAdapter } from './CoStarAdapter';
export { CrexiAdapter } from './CrexiAdapter';
export { LoopNetAdapter } from './LoopNetAdapter';
