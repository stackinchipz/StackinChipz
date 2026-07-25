/** Public library surface for programmatic use. */
export * from './types';
export * from './engine/analysis';
export * from './engine/finance';
export * from './engine/taxNormalizer';
export * from './engine/compSelector';
export * from './engine/buyAnalyzer';
export * from './engine/leaseAnalyzer';
export * from './engine/comparisonEngine';
export * from './engine/sensitivity';
export * from './engine/robotaxi';
export * from './providers';
export { ConsoleReporter } from './reporters/ConsoleReporter';
export { JsonReporter } from './reporters/JsonReporter';
export { HtmlReporter } from './reporters/HtmlReporter';
