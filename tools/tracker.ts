#!/usr/bin/env bun
// tracker.ts — application tracker. JSON is the source of truth
// (applications/tracker.json); CSV is an export for spreadsheets.
//
// Usage:
//   bun run tools/tracker.ts add --company "Acme" --role "Senior SWE" [--url URL] \
//       [--fit 82] [--status applied] [--source adzuna] [--notes "..."] \
//       [--deadline YYYY-MM-DD] [--resume PATH] [--cover PATH] [--contact NAME] \
//       [--location "City, ST"] [--date YYYY-MM-DD] [--upsert] [--json]
//   bun run tools/tracker.ts update --id 3 [--status interview] [--notes "replace"] \
//       [--append-note "text"] [--followup] [--date YYYY-MM-DD] [--deadline ...] \
//       [--resume PATH] [--cover PATH] [--contact NAME] [--url URL] [--fit N]
//   bun run tools/tracker.ts list [--status applied] [--open|--final] [--json]
//   bun run tools/tracker.ts find --company "acme" [--role "ml"] [--open] [--json]
//   bun run tools/tracker.ts quiet [--days 10] [--json]   # submitted, open, gone quiet
//   bun run tools/tracker.ts export                       # writes applications/tracker.csv
//
// Status vocabulary:
//   pre-submission (open, never chased): saved, drafted
//   submitted (open):                    applied, screen, interview, offer
//   final (closed):                      hired, rejected, no_response,
//                                        offer_declined, withdrawn
// Spaces/hyphens are normalized to underscores ("no response" -> no_response).
// Unknown statuses are accepted with a warning so old data keeps working.
//
// Notes: --append-note adds "YYYY-MM-DD: text" (dated, counts as contact for the
// days-quiet math); --followup appends "YYYY-MM-DD: followed up". `add --upsert`
// appends an *undated* "redrafted" marker, which deliberately does not count as
// contact with the employer.

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

interface AppRecord {
  id: number;
  date: string; // ISO date: drafted/added, overwritten with the submission date
  company: string;
  role: string;
  url: string;
  fit: number | null;
  status: string;
  source: string; // adzuna | ats | linkedin | manual | <url host>
  notes: string;
  updated: string;
  // Optional fields (added later; absent on older records).
  deadline?: string; // YYYY-MM-DD, only when the posting states one
  resume_file?: string;
  cover_letter_file?: string;
  contact?: string;
  location?: string;
}

const PRE = ["saved", "drafted"];
const SUBMITTED = ["applied", "screen", "interview", "offer"];
const FINAL = ["hired", "rejected", "no_response", "offer_declined", "withdrawn"];
const KNOWN = [...PRE, ...SUBMITTED, ...FINAL];
const ORDER: Record<string, number> = Object.fromEntries(
  [...PRE, ...SUBMITTED].map((s, i) => [s, i])
);

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

function str(v: string | boolean | undefined): string | undefined {
  return v === undefined || v === true ? undefined : String(v);
}

function normStatus(s: string): string {
  const n = s.trim().toLowerCase().replace(/[\s-]+/g, "_");
  if (!KNOWN.includes(n)) {
    console.error(
      `warning: unknown status "${s}" (known: ${KNOWN.join(", ")}); storing as "${n}"`
    );
  }
  return n;
}
function isFinal(s: string): boolean {
  return FINAL.includes(normStatus2(s));
}
// Silent normalization for reading stored values.
function normStatus2(s: string): string {
  return (s ?? "").trim().toLowerCase().replace(/[\s-]+/g, "_");
}

function isDate(s: string | undefined): boolean {
  return !!s && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(Date.parse(s));
}

function appendNote(rec: AppRecord, entry: string) {
  rec.notes = rec.notes ? `${rec.notes} | ${entry}` : entry;
}

/** Latest of the record date and any "YYYY-MM-DD:"-prefixed note entry. */
function lastContact(r: AppRecord): string {
  let last = isDate(r.date) ? r.date : "";
  const re = /(?:^|\|\s*)(\d{4}-\d{2}-\d{2}):/g;
  for (const m of (r.notes ?? "").matchAll(re)) {
    if (isDate(m[1]) && m[1] > last) last = m[1];
  }
  return last;
}
function daysSince(iso: string, today: string): number | null {
  if (!isDate(iso)) return null;
  return Math.floor((Date.parse(today) - Date.parse(iso)) / 86_400_000);
}
function followups(r: AppRecord): number {
  return ((r.notes ?? "").match(/followed up/gi) ?? []).length;
}

function sameApp(r: AppRecord, company: string, role: string): boolean {
  const n = (s: string) => s.trim().toLowerCase().replace(/\s+/g, " ");
  return n(r.company) === n(company) && n(r.role) === n(role);
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

function decorate(r: AppRecord, today: string) {
  const status = normStatus2(r.status);
  const submittedOpen = SUBMITTED.includes(status);
  const lc = lastContact(r);
  return {
    ...r,
    open: !FINAL.includes(status),
    days_quiet: submittedOpen ? daysSince(lc, today) : null,
    followups_sent: followups(r),
    last_contact: submittedOpen ? lc : null,
    days_to_deadline: r.deadline && isDate(r.deadline) ? -(daysSince(r.deadline, today) ?? 0) : null,
  };
}

function printTable(records: AppRecord[], today: string) {
  if (records.length === 0) {
    console.log("No applications tracked yet.");
    return;
  }
  for (const r of records) {
    const d = decorate(r, today);
    const extras: string[] = [];
    if (d.days_quiet != null) extras.push(`${d.days_quiet}d quiet`);
    if (d.followups_sent) extras.push(`${d.followups_sent} follow-up(s)`);
    if (r.deadline) {
      const dd = d.days_to_deadline;
      const mark = dd == null ? "" : dd < 0 ? " ⚠ passed" : dd <= 7 ? " 🔥" : "";
      extras.push(`deadline ${r.deadline}${mark}`);
    }
    console.log(
      `#${r.id} [${r.status}] ${r.company} — ${r.role}` +
        (r.fit != null ? ` (fit ${r.fit})` : "") +
        `\n    ${r.date}${r.source ? " · " + r.source : ""}${r.url ? " · " + r.url : ""}` +
        (extras.length ? `\n    ${extras.join(" · ")}` : "") +
        (r.resume_file || r.cover_letter_file
          ? `\n    files: ${[r.resume_file, r.cover_letter_file].filter(Boolean).join(", ")}`
          : "") +
        (r.notes ? `\n    note: ${r.notes}` : "")
    );
  }
}

function applyOptional(rec: AppRecord, flags: Record<string, string | boolean>) {
  const set = (flag: string, key: keyof AppRecord) => {
    const v = str(flags[flag]);
    if (v !== undefined) (rec as unknown as Record<string, unknown>)[key] = v;
  };
  set("url", "url");
  set("source", "source");
  set("resume", "resume_file");
  set("cover", "cover_letter_file");
  set("contact", "contact");
  set("location", "location");
  const dl = str(flags.deadline);
  if (dl !== undefined) {
    if (!isDate(dl)) {
      console.error(`--deadline must be YYYY-MM-DD (got "${dl}")`);
      process.exit(1);
    }
    rec.deadline = dl;
  }
  const fit = str(flags.fit);
  if (fit !== undefined) rec.fit = Number(fit);
}

function emit(json: boolean, data: unknown, human: () => void) {
  if (json) console.log(JSON.stringify(data, null, 2));
  else human();
}

// ---- main ----
const [cmd, ...rest] = process.argv.slice(2);
const flags = parseArgs(rest);
const records = await load();
const today = new Date().toISOString().slice(0, 10);
const json = flags.json === true;

const dateFlag = str(flags.date);
if (dateFlag !== undefined && !isDate(dateFlag)) {
  console.error(`--date must be YYYY-MM-DD (got "${dateFlag}")`);
  process.exit(1);
}

switch (cmd) {
  case "add": {
    if (!flags.company || !flags.role || flags.company === true || flags.role === true) {
      console.error("add requires --company and --role");
      process.exit(1);
    }
    const company = String(flags.company);
    const role = String(flags.role);
    const status = flags.status ? normStatus(String(flags.status)) : "applied";

    if (flags.upsert) {
      const open = records.filter((r) => sameApp(r, company, role) && !isFinal(r.status));
      if (open.length > 0) {
        const rec = open[open.length - 1];
        applyOptional(rec, flags);
        // Never move an open row backwards.
        const cur = normStatus2(rec.status);
        if (ORDER[status] !== undefined && ORDER[cur] !== undefined && ORDER[status] > ORDER[cur]) {
          rec.status = status;
        }
        if (PRE.includes(normStatus2(rec.status))) rec.date = dateFlag ?? today;
        appendNote(rec, "redrafted");
        rec.updated = today;
        await save(records);
        emit(json, rec, () =>
          console.log(`Updated open #${rec.id}: ${rec.company} — ${rec.role} [${rec.status}] (redrafted)`)
        );
        break;
      }
      const closed = records.filter((r) => sameApp(r, company, role) && isFinal(r.status));
      if (closed.length > 0 && !json) {
        console.log(
          `Note: earlier application(s) to this role are closed (${closed
            .map((r) => `#${r.id} ${r.status}`)
            .join(", ")}); adding a new row.`
        );
      }
    }

    const id = records.reduce((m, r) => Math.max(m, r.id), 0) + 1;
    const rec: AppRecord = {
      id,
      date: dateFlag ?? today,
      company,
      role,
      url: "",
      fit: null,
      status,
      source: "manual",
      notes: str(flags.notes) ?? "",
      updated: today,
    };
    applyOptional(rec, flags);
    records.push(rec);
    await save(records);
    emit(json, rec, () => console.log(`Added #${id}: ${rec.company} — ${rec.role} [${rec.status}]`));
    break;
  }
  case "update": {
    const id = Number(flags.id);
    const rec = records.find((r) => r.id === id);
    if (!rec) {
      console.error(`No application #${flags.id}`);
      process.exit(1);
    }
    if (flags.status && flags.status !== true) {
      const next = normStatus(String(flags.status));
      const prev = normStatus2(rec.status);
      // Moving off a pre-submission status: the date becomes the submission date.
      if (PRE.includes(prev) && !PRE.includes(next)) rec.date = dateFlag ?? today;
      else if (dateFlag) rec.date = dateFlag;
      rec.status = next;
    } else if (dateFlag) {
      rec.date = dateFlag;
    }
    if (str(flags.notes) !== undefined) rec.notes = String(flags.notes);
    const add = str(flags["append-note"]);
    if (add !== undefined) appendNote(rec, `${today}: ${add}`);
    if (flags.followup) appendNote(rec, `${today}: followed up`);
    applyOptional(rec, flags);
    rec.updated = today;
    await save(records);
    emit(json, rec, () => console.log(`Updated #${id} → [${rec.status}]`));
    break;
  }
  case "list": {
    let filtered = records;
    if (flags.status && flags.status !== true) {
      const s = normStatus2(String(flags.status));
      filtered = filtered.filter((r) => normStatus2(r.status) === s);
    }
    if (flags.open) filtered = filtered.filter((r) => !isFinal(r.status));
    if (flags.final) filtered = filtered.filter((r) => isFinal(r.status));
    emit(json, filtered.map((r) => decorate(r, today)), () => {
      printTable(filtered, today);
      console.log(`\n${filtered.length} of ${records.length} application(s).`);
    });
    break;
  }
  case "find": {
    const c = str(flags.company)?.toLowerCase();
    const ro = str(flags.role)?.toLowerCase();
    if (!c) {
      console.error("find requires --company (case-insensitive substring)");
      process.exit(1);
    }
    let hits = records.filter(
      (r) => r.company.toLowerCase().includes(c) && (!ro || r.role.toLowerCase().includes(ro))
    );
    if (flags.open) hits = hits.filter((r) => !isFinal(r.status));
    emit(json, hits.map((r) => decorate(r, today)), () => {
      printTable(hits, today);
      console.log(`\n${hits.length} match(es).`);
    });
    break;
  }
  case "quiet": {
    const days = flags.days && flags.days !== true ? Number(flags.days) : 10;
    const hits = records
      .map((r) => decorate(r, today))
      .filter((d) => d.days_quiet != null && d.days_quiet >= days)
      .sort((a, b) => (b.days_quiet ?? 0) - (a.days_quiet ?? 0));
    emit(json, hits, () => {
      if (hits.length === 0) console.log(`No submitted, open applications quiet for ${days}+ days.`);
      for (const d of hits) {
        console.log(
          `#${d.id} [${d.status}] ${d.company} — ${d.role} · ${d.days_quiet}d quiet · ` +
            `${d.followups_sent} follow-up(s) · last contact ${d.last_contact}` +
            (d.contact ? ` · contact ${d.contact}` : "")
        );
      }
    });
    break;
  }
  case "export": {
    // Original columns first (unchanged order), new optional columns appended.
    const header =
      "id,date,company,role,status,fit,source,url,notes,deadline,resume_file,cover_letter_file,contact,location,updated";
    const rows = records.map((r) =>
      [
        r.id,
        r.date,
        r.company,
        r.role,
        r.status,
        r.fit ?? "",
        r.source,
        r.url,
        r.notes,
        r.deadline ?? "",
        r.resume_file ?? "",
        r.cover_letter_file ?? "",
        r.contact ?? "",
        r.location ?? "",
        r.updated ?? "",
      ]
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
      "Usage: tracker.ts <add|update|list|find|quiet|export> [flags] (see file header)"
    );
    process.exit(1);
}
