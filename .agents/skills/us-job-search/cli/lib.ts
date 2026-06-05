// Shared helpers for the Adzuna-backed US job search CLI.

import { dirname, join, resolve } from "node:path";

export interface NormalizedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  posted: string; // ISO date
  url: string; // Adzuna redirect to original posting
  salary_min: number | null;
  salary_max: number | null;
  contract_time: string | null;
  description: string;
}

export interface SearchCache {
  query: string;
  location: string;
  fetched_at: string;
  count: number; // total matches reported by Adzuna
  results: NormalizedJob[];
}

/** Repo root, derived relative to this file (.agents/skills/us-job-search/cli/lib.ts). */
export function repoRoot(): string {
  // import.meta.dir -> .../.agents/skills/us-job-search/cli
  const here = (import.meta as unknown as { dir: string }).dir;
  return resolve(here, "..", "..", "..", "..");
}

export function cachePath(): string {
  return join(repoRoot(), "job_scraper", "latest-search.json");
}

export function requireKeys(): { appId: string; appKey: string } {
  const appId = process.env.ADZUNA_APP_ID;
  const appKey = process.env.ADZUNA_APP_KEY;
  if (!appId || !appKey) {
    console.error(
      "Missing ADZUNA_APP_ID / ADZUNA_APP_KEY. Get free keys at " +
        "https://developer.adzuna.com/ and export them before running."
    );
    process.exit(1);
  }
  return { appId, appKey };
}

/** Minimal flag parser: positional args + `--flag value` / `--bool`. */
export function parseArgs(argv: string[]): {
  positional: string[];
  flags: Record<string, string | boolean>;
} {
  const positional: string[] = [];
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith("--")) {
        flags[key] = true;
      } else {
        flags[key] = next;
        i++;
      }
    } else {
      positional.push(a);
    }
  }
  return { positional, flags };
}

export function normalize(raw: any): NormalizedJob {
  return {
    id: String(raw.id ?? ""),
    title: raw.title ?? "",
    company: raw.company?.display_name ?? "",
    location: raw.location?.display_name ?? "",
    posted: raw.created ?? "",
    url: raw.redirect_url ?? "",
    salary_min: typeof raw.salary_min === "number" ? raw.salary_min : null,
    salary_max: typeof raw.salary_max === "number" ? raw.salary_max : null,
    contract_time: raw.contract_time ?? null,
    description: (raw.description ?? "").replace(/\s+/g, " ").trim(),
  };
}

export { dirname };
