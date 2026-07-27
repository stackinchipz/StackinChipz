/** Serializes an AnalysisResult to JSON (string or file). */
import { writeFileSync } from 'fs';
import { AnalysisResult } from '../types';

export class JsonReporter {
  serialize(result: AnalysisResult): string {
    return JSON.stringify(result, null, 2);
  }

  write(result: AnalysisResult, path: string): void {
    writeFileSync(path, this.serialize(result), 'utf-8');
  }
}
