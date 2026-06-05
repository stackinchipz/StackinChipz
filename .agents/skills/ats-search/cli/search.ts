#!/usr/bin/env bun
// search.ts — fetch postings directly from companies' Greenhouse/Lever boards.
//
// No API keys, no scraping — these are official public JSON endpoints.
//
// Usage:
//   bun run search.ts [--query "<keywords>"] [--location "<substring>"]
//       [--remote] [--companies <path>]

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

interface NormalizedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  posted: string;
  url: string;
  source: "greenhouse" | "lever";
  description: string;
}

interface CompanyRef {
  token: string;
  name?: string;
}
interface CompaniesConfig {
  greenhouse?: CompanyRef[];
  lever?: CompanyRef[];
}

function here(): string {
  return (import.meta as unknown as { dir: string }).dir;
}
function repoRoot(): string {
  // .agents/skills/ats-search/cli -> repo root
  return resolve(here(), "..", "..", "..", "..");
}

function parseArgs(argv: string[]) {
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) continue;
    const key = a.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) flags[key] = true;
    else {
      flags[key] = next;
      i++;
    }
  }
  return flags;
}

function stripHtml(html: string): string {
  return html
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z]+;/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

async function fetchJson(url: string): Promise<any | null> {
  try {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) {
      console.error(`  ! ${res.status} for ${url}`);
      return null;
    }
    return await res.json();
  } catch (err) {
    console.error(`  ! network error for ${url}:`, err);
    return null;
  }
}

async function fetchGreenhouse(c: CompanyRef): Promise<NormalizedJob[]> {
  const url = `https://boards-api.greenhouse.io/v1/boards/${c.token}/jobs?content=true`;
  const data = await fetchJson(url);
  if (!data?.jobs) return [];
  return data.jobs.map((j: any) => ({
    id: `gh-${c.token}-${j.id}`,
    title: j.title ?? "",
    company: c.name ?? c.token,
    location: j.location?.name ?? "",
    posted: j.updated_at ?? "",
    url: j.absolute_url ?? "",
    source: "greenhouse" as const,
    description: stripHtml(j.content ?? ""),
  }));
}

async function fetchLever(c: CompanyRef): Promise<NormalizedJob[]> {
  const url = `https://api.lever.co/v0/postings/${c.token}?mode=json`;
  const data = await fetchJson(url);
  if (!Array.isArray(data)) return [];
  return data.map((j: any) => ({
    id: `lv-${c.token}-${j.id}`,
    title: j.text ?? "",
    company: c.name ?? c.token,
    location: j.categories?.location ?? "",
    posted: j.createdAt ? new Date(j.createdAt).toISOString() : "",
    url: j.hostedUrl ?? "",
    source: "lever" as const,
    description: (j.descriptionPlain ?? "").replace(/\s+/g, " ").trim(),
  }));
}

// ---- main ----
const flags = parseArgs(process.argv.slice(2));

const configPath = flags.companies
  ? resolve(String(flags.companies))
  : join(here(), "..", "companies.json");

let config: CompaniesConfig;
try {
  config = JSON.parse(await readFile(configPath, "utf8"));
} catch {
  console.error(
    `No company list found at ${configPath}.\n` +
      `Copy companies.example.json to companies.json and add your target boards.`
  );
  process.exit(1);
}

const targets: Array<[CompanyRef, "greenhouse" | "lever"]> = [
  ...(config.greenhouse ?? []).map((c) => [c, "greenhouse"] as const),
  ...(config.lever ?? []).map((c) => [c, "lever"] as const),
];

if (targets.length === 0) {
  console.error("companies.json has no greenhouse/lever entries.");
  process.exit(1);
}

console.log(`Fetching ${targets.length} board(s)...`);
const batches = await Promise.all(
  targets.map(([c, src]) => {
    console.log(`  - ${src}: ${c.name ?? c.token}`);
    return src === "greenhouse" ? fetchGreenhouse(c) : fetchLever(c);
  })
);

let jobs = batches.flat();

// De-dupe by id.
const seen = new Set<string>();
jobs = jobs.filter((j) => (seen.has(j.id) ? false : (seen.add(j.id), true)));

// Client-side filters.
const q = flags.query ? String(flags.query).toLowerCase() : null;
const loc = flags.location ? String(flags.location).toLowerCase() : null;
if (q) jobs = jobs.filter((j) => j.title.toLowerCase().includes(q));
if (loc) jobs = jobs.filter((j) => j.location.toLowerCase().includes(loc));
if (flags.remote) jobs = jobs.filter((j) => /remote/i.test(j.location));

// Cache.
const outPath = join(repoRoot(), "job_scraper", "ats-search.json");
await mkdir(dirname(outPath), { recursive: true });
await writeFile(
  outPath,
  JSON.stringify(
    { fetched_at: new Date().toISOString(), count: jobs.length, results: jobs },
    null,
    2
  ),
  "utf8"
);

console.log(`\n${jobs.length} posting(s)` + (q ? ` matching "${q}"` : "") + ":\n");
for (const j of jobs) {
  console.log(`${j.id}  ${j.title}\n    ${j.company} · ${j.location || "—"} · ${j.posted.slice(0, 10)}\n    ${j.url}`);
}
console.log(`\nCached → ${outPath}`);
