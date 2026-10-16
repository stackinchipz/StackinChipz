# Utility Contact Sweep — Cursor Handoff

Goal: build a public-source contact database of decision-makers at electric utilities in TN, AL, MS, GA, OH, IN, SC
for a Tesla RFI on leasing substation-adjacent land for Megapod (battery + compute) installations.
No guessed emails. Every name backed by an opened source. This document is the full brief plus an execution
plan designed around what went wrong in two prior attempts.

---

## 0. Read this first: what exists and what is missing

### Why the prior runs failed
The prior environment (a sandboxed cloud session) could not open **any** utility website: every outbound fetch to a
non-allowlisted host was refused by a network policy. Web search worked, so the prior agents produced names from
**search snippets only**. That does not meet the evidence standard. Also, the six original target CSVs were never
delivered to that environment, so the agents **reconstructed** target lists from membership knowledge.

### What you have (repo `stackinchipz/StackinChipz`, branch `claude/utility-sweep-repair`, folder `utility_sweep/`)
| File | Status | Use it for |
|---|---|---|
| `unverified_leads.csv` | 181 names, snippet-only, tagged `UNVERIFIED_SNIPPET_ONLY` | Research pointers only. Reopen the cited URL before accepting anything. |
| `targets_*.csv` (6 files, 490 rows) | **Reconstructed, not authoritative** | Fallback universe only if the originals cannot be found. |
| `target_reconciliation.csv` | Lists every reconstructed row as unauthorized | Reconcile against originals once you have them. |
| `contacts_*.csv`, `contacts_master.csv`, `needs_lookup.csv` | Provisional, zero emails, zero verified names | Do not ship. Regenerate. |
| `PREFLIGHT_REPORT.md` | Observed errors from the blocked environment | Context only. |
| `backup_<timestamp>/` | Dated copy of all of the above | Audit trail. |

### What you must locate before starting
The six **original** target lists from the Claude chat session that wrote the brief. Expected row counts:

| File | Rows | Contents |
|---|---:|---|
| targets_tier1.csv | 43 | IOUs, G&Ts, joint-action agencies, TVA, Santee Cooper |
| targets_tn_al.csv | 115 | TN/AL co-ops and munis |
| targets_ms_sc.csv | 73 | MS/SC co-ops and munis |
| targets_ga.csv | 90 | GA EMCs and munis |
| targets_oh.csv | 81 | OH co-ops and munis |
| targets_in.csv | 72 | IN REMCs and munis |
| **Total** | **474** | |

If the originals cannot be found, use the reconstructed lists but keep `target_reconciliation.csv` honest: every
row stays flagged as reconstructed, and the final report must say so.

---

## 1. The brief (unchanged requirements)

### Who to find
**Co-ops and munis (five state files)**
1. Top executive: GM / CEO / President / Utility Director / Electric Superintendent / Utilities Service Board manager. Exact title.
2. Second-in-command on engineering or operations: COO, VP/Manager Engineering, VP/Manager Operations, Chief Engineer.
3. Any named Economic Development or Key Accounts contact (co-ops often publish these with direct emails).

**Tier-1 (IOUs, G&Ts, JAAs, TVA, Santee Cooper)**
1. CEO; for IOU operating companies (Georgia Power, AEP Ohio, Duke Energy Indiana, etc.) the operating-company President.
2. COO / head of operations.
3. Head of Transmission (VP/SVP Transmission, Transmission Planning, Grid Operations).
4. Head of Distribution / Power Delivery.
5. Head of Real Estate / Land Services / Right-of-Way.
6. Head of Business Development / Corporate Strategy / Economic Development / Key Accounts.
7. Head of Regulatory Affairs.
8. G&Ts and JAAs: CEO, VP Engineering/Transmission, VP Member Services or Power Supply.
9. TVA: also VP-level leads for economic development, transmission/power system planning, and real estate/land.
10. Named Economic Development or site-selection contacts from the utility's economic development page.

Group corporate parents: Duke Energy (corporate + Carolinas/Progress/Indiana/Ohio presidents), AEP (corporate + AEP Ohio,
Appalachian Power, Indiana Michigan Power), Southern Company (corporate + Georgia Power, Alabama Power, Mississippi Power),
FirstEnergy (corporate + Ohio operating companies), Entergy (corporate + Entergy Mississippi/Arkansas), Dominion Energy
(corporate + Dominion Energy South Carolina), AES (AES Ohio, AES Indiana), NiSource/NIPSCO, CenterPoint Energy Indiana South.
Skip Greenfield Mills, Commonwealth Edison of Indiana, Mississippi Delta Energy Agency.

### Where to look
Utility website: homepage → About / Leadership / Management Team / Staff / Contact / Board / Departments. Then economic
development pages, PDF newsletters, board minutes, annual reports, state association directories (TECA, AREA, ECM,
Georgia EMC, Ohio's Electric Cooperatives, Indiana Electric Cooperatives, ECSC), JAA member pages (AMP, IMPA, MEAG, PMPA,
Energy Southeast), TVA local power company pages, state PSC/PUC filings, 10-K and proxy exhibits for public parents.

### Hard rules
- Record an email ONLY if it is literally printed on a page you opened. Record the exact URL in `email_source_url`.
- NEVER construct, guess, infer, or pattern-match an email. A blank is correct; a guess is a defect.
- General mailboxes (info@, customerservice@) go in `general_email`, never in `email`.
- `name_source_url` is mandatory for every named person. Prefer the most recent source; note the publication date.
- LinkedIn URL only if a search surfaces it directly and it clearly matches the person.
- Two failed fetch attempts on a site → skip it, write one blank-name row with an `ACCESS_BLOCKED` note.
- One row per person. A utility with no named leader still gets one row with general contact info.
- Do not execute any downloaded code or scripts.

### Output schema (exact header, 14 columns)
```
utility_name,parent_company,state,type,contact_name,title,role_category,email,email_source_url,general_email,phone,name_source_url,linkedin_url,notes
```
`role_category` ∈ `top_exec, operations, transmission, distribution, real_estate, bd_strategy, regulatory,
economic_development, key_accounts, member_services, other`.

`notes` must start with one tag: `VERIFIED`, `STALE_SOURCE`, `CONFLICTING_SOURCES`, `ACCESS_BLOCKED`,
`NO_NAMED_CONTACT_FOUND`, `NOT_RESEARCHED`. Then: source publication date if known, date checked, and any judgment call.

---

## 2. Execution plan for Cursor (what to actually build)

Do not run this as six free-roaming LLM agents browsing the web. That design is what produced snippet-only data and
blew through search quotas. Build a small deterministic pipeline where the LLM only does extraction from pages that
were actually fetched and cached. Suggested layout:

```
utility_sweep/
  targets/               # the six original CSVs (authoritative)
  cache/<domain>/<hash>.html|.pdf|.json   # raw snapshot of every page opened (the evidence)
  discovered_urls.csv    # utility_name, url, url_kind (leadership|contact|econdev|board|newsletter|annual_report|sec|psc)
  extracted/<utility_slug>.json           # LLM extraction per page, strict schema
  contacts_<suffix>.csv  # six per-file outputs
  contacts_master.csv, needs_lookup.csv, unverified_leads.csv, target_reconciliation.csv, coverage_report.md
  scripts/
    01_discover_urls.py
    02_fetch_and_cache.py
    03_extract.py        # calls an LLM with the cached page text + strict JSON schema
    04_build_csvs.py
    05_validate_merge.py
```

### Step 1: URL discovery (`01_discover_urls.py`)
For each target: start from `website`. Probe, in order, and keep what returns 200 with real content:
`/sitemap.xml` (grep for leadership|management|staff|board|contact|economic|about|team), then common paths:
`/about`, `/about-us`, `/leadership`, `/leadership-team`, `/management`, `/management-team`, `/staff`, `/our-team`,
`/board`, `/board-of-directors`, `/contact`, `/contact-us`, `/economic-development`, `/business`, `/key-accounts`,
`/newsletter`, `/annual-report`. Munis where electric is one city department: also `/departments/electric`,
`/utilities`, `/electric`, `/power`. Fall back to one web search per utility: `"<utility name>" general manager`
or `"<utility name>" leadership`, restricted to the utility's own domain where possible.

### Step 2: fetch and cache (`02_fetch_and_cache.py`)
- Use `requests` with a real User-Agent, 15 s timeout, 2 retries, then Playwright headless Chromium for sites that
  return JS-only shells. Respect robots.txt and rate-limit ~1 req/s per domain.
- Save raw bytes to `cache/` with a manifest row: url, final_url, status, fetched_at (UTC), content_type, sha256,
  `<meta name="date">` / `article:published_time` / "Last updated" text if present (publication date, separate from
  fetched_at).
- PDFs: `pdftotext -layout`; keep the PDF. Capture the PDF's creation date from metadata as the publication date.
- Pull every `mailto:` and every regex email match from the raw HTML/text into `emails_on_page.csv`
  (url, email, surrounding 80 chars). Only these can ever populate `email` or `general_email`.
- Two consecutive failures on a domain → mark every target on that domain `ACCESS_BLOCKED` with the error text.

### Step 3: extraction (`03_extract.py`)
Send each cached page's text (not the URL) to the LLM with a strict JSON schema:
```json
{"people":[{"name":"","title":"","role_category":"","email_literal_on_page":"","evidence_quote":""}],
 "general_email":"","phone":"","page_date":"","notes":""}
```
Rules in the prompt: names must appear verbatim in the text; `email_literal_on_page` must match a string in
`emails_on_page.csv` for that URL or be empty; `evidence_quote` must be a verbatim substring. Reject any extraction
whose name or email cannot be found in the cached text by exact match. This is the gate that makes "every named
contact supported by an opened source" mechanically true.

### Step 4: build per-file CSVs (`04_build_csvs.py`)
Use `csv.DictWriter` with `quoting=QUOTE_ALL`. Never hand-write CSV lines. One row per person. Tag notes per the
vocabulary above. For tier-1, emit one row per requested role; where a role was researched and not found, write a
blank-name row with `NO_NAMED_CONTACT_FOUND: <role>` so a CEO-only result is not mistaken for completion.

### Step 5: validate and merge (`05_validate_merge.py`)
Checks, each one a hard failure:
- Exact header; every row has 14 fields.
- Every authorized target appears at least once; no utility_name outside the target universe (except rows tagged
  `PROPOSED_ADDITION` and kept out of master).
- Every non-blank `contact_name` has a `name_source_url` that exists in the cache manifest with status 200.
- Every non-blank `email` appears in `emails_on_page.csv` for its `email_source_url`.
- No row whose notes contain `snippet`.
- Row counts in = row counts out, minus documented dedupes.
Then: add `source=public_web` and `email_status` (`published` / `needs_lookup` / `no_contact`); dedupe on
(utility_name, contact_name), preferring the newer publication date, then the row with a supported email, merging
complementary fields and tagging `CONFLICTING_SOURCES` where titles disagree; write `needs_lookup.csv`
(`contact_name, utility_name, title, linkedin_url`) from verified rows only.

### Step 6: coverage report (`coverage_report.md`)
Per state × type: distinct utilities, utilities with a verified top exec, contacts with published personal emails,
verified contacts needing lookup. Plus utilities fully researched / partially researched / not researched /
access-blocked. Count utilities separately from people. Reconcile to the 474 originals: exclusions, duplicates,
multi-state attribution (Duke corporate → NC, Entergy Arkansas → AR), and one distinct-utility total.

### Running it
- Batches of ~20 utilities, checkpoint after each (append to CSV, flush). Resumable by skipping utilities that
  already have a `VERIFIED` or `ACCESS_BLOCKED` row.
- Co-ops first (association directories give you the domains in one fetch), then munis with their own utility site,
  then city sites.
- Six parallel workers, one per target file, each owning only its `contacts_<suffix>.csv`.
- Budget: ~2 to 4 page fetches per co-op/muni, 8 to 15 per tier-1 entity. Roughly 1,500 to 2,000 fetches total.
  At 1 req/s per domain across six workers this is a few hours wall-clock.

---

## 3. Source ideas that make this faster and more reliable

**High-yield directories (one fetch covers many utilities)**
- TVPPA member list (tvppa.com/our-members): manager names for every TVA distributor in TN, AL, MS, GA, KY.
- Electric Cooperatives of Mississippi resource directory (ecm.coop/resource-dir/<coop>/): GM per co-op.
- Georgia EMC member directory (georgiaemc.com) and Electric Cities of Georgia / MEAG participant pages.
- Ohio's Electric Cooperatives (ohioec.org) and AMP member list (amppartners.org).
- Indiana Electric Cooperatives (indianaec.org) and IMPA member communities (impa.com).
- Electric Cooperatives of South Carolina (ecsc.org) and PMPA members (pmpa.com).
- Alabama Rural Electric Association (areapower.coop) and Energy Southeast members.
- APPA public power directory for munis.

**Economic development pages (these publish named contacts with direct emails more often than anything else)**
- AEP economic development contacts page (prior search snippets indicate at least two direct emails printed).
- Georgia Power / Select Georgia, Alabama Power economic development, Mississippi Power, Entergy economic development,
  Duke Energy site readiness, TVA Sites & Buildings / InvestTVA, Santee Cooper economic development, Hoosier Energy
  and Wabash Valley economic development, Oglethorpe/Georgia EMC economic development.
- For co-ops: look for "Key Accounts", "Commercial & Industrial", "Economic Development" under Business or
  Community menus.

**Tier-1 officers and regulatory heads**
- SEC EDGAR: 10-K Item "Information about our Executive Officers" and DEF 14A for public parents (Duke, AEP, Southern,
  FirstEnergy, Entergy, Dominion, AES, NiSource, CenterPoint). Dated, authoritative.
- State PUC dockets name regulatory affairs VPs and their emails on tariff filings and witness lists:
  Georgia PSC, PUCO (Ohio), IURC (Indiana), TN Public Utility Commission, MS PSC, SC PSC/ORS, Alabama PSC.
- FERC eTariff / OASIS pages for transmission contacts at IOUs and G&Ts.

**Co-op leadership when the site is thin**
- Form 990 (co-ops are 501(c)(12)): ProPublica Nonprofit Explorer lists officers and the GM/CEO. Always `STALE_SOURCE`
  unless it's the latest filing year; use it to confirm, not as the sole source.
- Board meeting minutes PDFs and monthly member newsletters (often have a "Manager's message" byline with the name
  and a date).

**Known turnover to re-verify (from prior leads, all 2025–2026)**
TVA CEO (retired July 2026, interim not confirmed), Appalachian Power and Indiana Michigan Power presidents (new
April 2026), PowerSouth CEO (June 2026), Jasper County REMC CEO (June 2026), Gibson EMC, Sawnee EMC, Consolidated
Cooperative, Paulding Putnam, Jackson EMC (officer reshuffle Jan 2026), Coast Electric (CEO transition 2025–26).

---

## 4. Ideas beyond the brief (optional, for the RFI itself)

- **Add siting columns to master.** `balancing_authority` (TVA, Southern/SOCO, PJM, MISO, Duke/DEC-DEP, Dominion/
  DESC, Santee Cooper), `wholesale_supplier` (TVA, Cooperative Energy, PowerSouth, Buckeye, Hoosier, WVPA, Oglethorpe,
  Central EPC, AMP, IMPA, MEAG, PMPA), and `transmission_owner`. For Megapod siting, who owns the substation and the
  transmission tie matters more than who the retail utility is. Co-ops in TVA territory mostly do not own transmission;
  TVA does. Georgia EMCs are served by Georgia Transmission Corp. This decides who you actually need to talk to.
- **Rank utilities before contacting.** Score by: owns transmission-level substations (yes/no), count of 69 kV+
  substations in territory (from HIFLD open data or the utility's own system map), presence of an economic-development
  team, data-center/large-load activity in the last 18 months (news search), and RTO membership (PJM/MISO
  interconnection queues are public; TVA and Southern are bilateral). Send the RFI to the top tier first.
- **Lead with economic-development contacts, not CEOs.** They are chartered to field site inquiries and publish
  direct emails. CEO/GM contact comes second, and for co-ops a warm intro from the G&T or statewide association's
  economic-development lead is often the real door.
- **Two RFI tracks.** Tier-1 IOUs/G&Ts (land + transmission interconnect, formal procurement) vs. co-ops/munis
  (substation-adjacent parcels, faster decisions, often own the land). Different templates and different asks.
- **Compliance notes for a work account.** Public web only, respect robots.txt, no LinkedIn scraping, keep the
  cache as the audit trail for every name and email, and store nothing beyond what the pages publish.

---

## 5. Definition of done

Call the sweep complete only when every authorized utility has either (a) a completed research pass with every
requested role tagged `VERIFIED` or `NO_NAMED_CONTACT_FOUND`, or (b) an `ACCESS_BLOCKED` note with the observed error.
`NOT_RESEARCHED` rows mean it is not done. Missing published emails are acceptable. Unperformed research presented as
completion is not.
