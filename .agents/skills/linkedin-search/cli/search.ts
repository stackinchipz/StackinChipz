#!/usr/bin/env bun
// search.ts — LinkedIn-sourced jobs via Google Jobs (SerpApi).
//
// Google Jobs aggregates LinkedIn listings, so this gets LinkedIn coverage in
// bulk without scraping LinkedIn directly (ToS-safe).
//
// Usage:
//   bun run search.ts "<query>" [--location "City, ST"] [--linkedin-only]
//       [--remote] [--next-page-token <token>]

import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

interface NormalizedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  posted: string;
  url: string;
  via: string;
  description: string;
}

function repoRoot(): string {
  // .agents/skills/linkedin-search/cli -> repo root
  return resolve((import.meta as unknown as { dir: string }).dir, "..", "..", "..", "..");
}

function parseArgs(argv: string[]) {
  const positional: string[] = [];
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith("--")) flags[key] = true;
      else {
        flags[key] = next;
        i++;
      }
    } else positional.push(a);
  }
  return { positional, flags };
}

function linkedinApplyUrl(j: any): string | null {
  for (const opt of j.apply_options ?? []) {
    if (/linkedin\.com/i.test(opt.link ?? "")) return opt.link;
  }
  if (/linkedin/i.test(j.via ?? "") && j.share_link) return j.share_link;
  return null;
}

// ---- main ----
const { positional, flags } = parseArgs(process.argv.slice(2));
const query = positional.join(" ").trim();
if (!query) {
  console.error('Usage: bun run search.ts "<query>" [--location "City, ST"] [--linkedin-only] ...');
  process.exit(1);
}

const apiKey = process.env.SERPAPI_KEY;
if (!apiKey) {
  console.error("Missing SERPAPI_KEY. Get one at https://serpapi.com/ and export it.");
  process.exit(1);
}

const params = new URLSearchParams({
  engine: "google_jobs",
  q: query,
  api_key: apiKey,
});
if (flags.location) params.set("location", String(flags.location));
if (flags["next-page-token"]) params.set("next_page_token", String(flags["next-page-token"]));

let data: any;
try {
  const res = await fetch(`https://serpapi.com/search.json?${params.toString()}`);
  if (!res.ok) {
    console.error(`SerpApi error ${res.status}: ${await res.text()}`);
    process.exit(1);
  }
  data = await res.json();
} catch (err) {
  console.error("Network error calling SerpApi:", err);
  process.exit(1);
}

if (data.error) {
  console.error(`SerpApi: ${data.error}`);
  process.exit(1);
}

let jobs: NormalizedJob[] = (data.jobs_results ?? []).map((j: any) => {
  const lkUrl = linkedinApplyUrl(j);
  return {
    id: String(j.job_id ?? j.share_link ?? `${j.title}-${j.company_name}`),
    title: j.title ?? "",
    company: j.company_name ?? "",
    location: j.location ?? "",
    posted: j.detected_extensions?.posted_at ?? "",
    url: lkUrl ?? j.share_link ?? j.apply_options?.[0]?.link ?? "",
    via: j.via ?? "",
    description: (j.description ?? "").replace(/\s+/g, " ").trim(),
  };
});

if (flags["linkedin-only"]) {
  jobs = jobs.filter((j) => /linkedin/i.test(j.via) || /linkedin\.com/i.test(j.url));
}
if (flags.remote) {
  jobs = jobs.filter((j) => /remote/i.test(j.location) || /remote/i.test(j.title));
}

const outPath = join(repoRoot(), "job_scraper", "linkedin-search.json");
await mkdir(dirname(outPath), { recursive: true });
await writeFile(
  outPath,
  JSON.stringify(
    {
      query,
      fetched_at: new Date().toISOString(),
      count: jobs.length,
      next_page_token: data.serpapi_pagination?.next_page_token ?? null,
      results: jobs,
    },
    null,
    2
  ),
  "utf8"
);

console.log(`\n${jobs.length} result(s) for "${query}"` + (flags["linkedin-only"] ? " (LinkedIn only)" : "") + ":\n");
for (const j of jobs) {
  console.log(`${j.title}\n    ${j.company} · ${j.location || "—"} · ${j.posted || "—"} · via ${j.via || "—"}\n    ${j.url}`);
}
console.log(`\nCached → ${outPath}`);
const token = data.serpapi_pagination?.next_page_token;
if (token) console.log(`Next page: --next-page-token ${token}`);
