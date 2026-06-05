#!/usr/bin/env bun
// search.ts — query the Adzuna US jobs API, normalize, cache, and print.
//
// Usage:
//   bun run search.ts "<query>" [--location "City, ST"] [--max-days N]
//       [--page N] [--results-per-page N] [--salary-min N] [--full-time]
//       [--distance KM] [--sort relevance|date|salary]

import { mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";
import {
  cachePath,
  normalize,
  parseArgs,
  requireKeys,
  type NormalizedJob,
  type SearchCache,
} from "./lib.ts";

const { positional, flags } = parseArgs(process.argv.slice(2));
const query = positional.join(" ").trim();

if (!query) {
  console.error('Usage: bun run search.ts "<query>" [--location "City, ST"] [--max-days N] ...');
  process.exit(1);
}

const { appId, appKey } = requireKeys();

const page = Number(flags.page ?? 1);
const params = new URLSearchParams({
  app_id: appId,
  app_key: appKey,
  what: query,
  results_per_page: String(flags["results-per-page"] ?? 20),
  "content-type": "application/json",
});

if (flags.location) params.set("where", String(flags.location));
if (flags.distance) params.set("distance", String(flags.distance));
if (flags["max-days"]) params.set("max_days_old", String(flags["max-days"]));
if (flags["salary-min"]) params.set("salary_min", String(flags["salary-min"]));
if (flags["full-time"]) params.set("full_time", "1");
if (flags.sort) params.set("sort_by", String(flags.sort));

const url = `https://api.adzuna.com/v1/api/jobs/us/search/${page}?${params.toString()}`;

let payload: any;
try {
  const res = await fetch(url);
  if (!res.ok) {
    console.error(`Adzuna API error ${res.status}: ${await res.text()}`);
    process.exit(1);
  }
  payload = await res.json();
} catch (err) {
  console.error("Network error calling Adzuna:", err);
  process.exit(1);
}

const results: NormalizedJob[] = (payload.results ?? []).map(normalize);

const cache: SearchCache = {
  query,
  location: String(flags.location ?? ""),
  fetched_at: new Date().toISOString(),
  count: Number(payload.count ?? results.length),
  results,
};

const outPath = cachePath();
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(cache, null, 2), "utf8");

// Compact human-readable summary.
const fmtSalary = (j: NormalizedJob) =>
  j.salary_min || j.salary_max
    ? `$${Math.round((j.salary_min ?? j.salary_max ?? 0) / 1000)}k-$${Math.round(
        (j.salary_max ?? j.salary_min ?? 0) / 1000
      )}k`
    : "—";

console.log(`\n${results.length} of ~${cache.count} matches for "${query}"` +
  (cache.location ? ` in ${cache.location}` : "") + ` (page ${page})\n`);

for (const j of results) {
  console.log(
    `${j.id}  ${j.title}\n    ${j.company} · ${j.location} · ${fmtSalary(j)} · ${j.posted.slice(0, 10)}\n    ${j.url}`
  );
}

console.log(`\nCached → ${outPath}`);
console.log(`Run: bun run detail.ts <id>  for a single record.`);
