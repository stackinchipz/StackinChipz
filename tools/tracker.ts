#!/usr/bin/env bun
// tracker.ts — application tracker. JSON is the source of truth
// (applications/tracker.json); CSV is an export for spreadsheets.
//
// Usage:
//   bun run tracker.ts add --company "Acme" --role "Senior SWE" [--url URL] \
//       [--fit 82] [--status applied] [--source adzuna] [--notes "..."]
//   bun run tracker.ts list [--status applied]
//   bun run tracker.ts update --id 3 [--status interview] [--notes "..."]
//   bun run tracker.ts export        # writes applications/tracker.csv
//
// Status vocabulary (suggested): saved, applied, screen, interview, offer,
// rejected, withdrawn.

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

interface AppRecord {
  id: number;
  date: string; // ISO date applied/added
  company: string;
  role: string;
  url: string;
  fit: number | null;
  status: string;
  source: string; // adzuna | ats | linkedin | manual
  notes: string;
  updated: string;
}

function repoRoot(): string {
  // tools/ -> repo root
  return resolve((import.meta as unknown as { dir: string }).dir, "..");
}
function dataPath(): string {
  return join(repoRoot(), "applications", "tracker.json");
}
function csvPath(): string {
  return join(repoRoot(), "applications", "tracker.csv");
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

async function load(): Promise<AppRecord[]> {
  try {
    return JSON.parse(await readFile(dataPath(), "utf8"));
  } catch {
    return [];
  }
}
async function save(records: AppRecord[]): Promise<void> {
  const p = dataPath();
  await mkdir(dirname(p), { recursive: true });
  await writeFile(p, JSON.stringify(records, null, 2), "utf8");
}

function csvEscape(v: string): string {
  return /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
}

function printTable(records: AppRecord[]) {
  if (records.length === 0) {
    console.log("No applications tracked yet.");
    return;
  }
  for (const r of records) {
    console.log(
      `#${r.id} [${r.status}] ${r.company} — ${r.role}` +
        (r.fit != null ? ` (fit ${r.fit})` : "") +
        `\n    ${r.date}${r.source ? " · " + r.source : ""}${r.url ? " · " + r.url : ""}` +
        (r.notes ? `\n    note: ${r.notes}` : "")
    );
  }
}

// ---- main ----
const [cmd, ...rest] = process.argv.slice(2);
const flags = parseArgs(rest);
const records = await load();
const today = new Date().toISOString().slice(0, 10);

switch (cmd) {
  case "add": {
    if (!flags.company || !flags.role) {
      console.error("add requires --company and --role");
      process.exit(1);
    }
    const id = records.reduce((m, r) => Math.max(m, r.id), 0) + 1;
    const rec: AppRecord = {
      id,
      date: today,
      company: String(flags.company),
      role: String(flags.role),
      url: flags.url ? String(flags.url) : "",
      fit: flags.fit != null && flags.fit !== true ? Number(flags.fit) : null,
      status: flags.status ? String(flags.status) : "applied",
      source: flags.source ? String(flags.source) : "manual",
      notes: flags.notes ? String(flags.notes) : "",
      updated: today,
    };
    records.push(rec);
    await save(records);
    console.log(`Added #${id}: ${rec.company} — ${rec.role} [${rec.status}]`);
    break;
  }
  case "update": {
    const id = Number(flags.id);
    const rec = records.find((r) => r.id === id);
    if (!rec) {
      console.error(`No application #${flags.id}`);
      process.exit(1);
    }
    if (flags.status) rec.status = String(flags.status);
    if (flags.notes) rec.notes = String(flags.notes);
    if (flags.fit != null && flags.fit !== true) rec.fit = Number(flags.fit);
    rec.updated = today;
    await save(records);
    console.log(`Updated #${id} → [${rec.status}]`);
    break;
  }
  case "list": {
    const filtered = flags.status
      ? records.filter((r) => r.status === String(flags.status))
      : records;
    printTable(filtered);
    console.log(`\n${filtered.length} of ${records.length} application(s).`);
    break;
  }
  case "export": {
    const header = "id,date,company,role,status,fit,source,url,notes";
    const rows = records.map((r) =>
      [r.id, r.date, r.company, r.role, r.status, r.fit ?? "", r.source, r.url, r.notes]
        .map((v) => csvEscape(String(v)))
        .join(",")
    );
    const p = csvPath();
    await mkdir(dirname(p), { recursive: true });
    await writeFile(p, [header, ...rows].join("\n") + "\n", "utf8");
    console.log(`Exported ${records.length} record(s) → ${p}`);
    break;
  }
  default:
    console.error(
      "Usage: tracker.ts <add|list|update|export> [flags] (see file header)"
    );
    process.exit(1);
}
