---
description: Clear generated profile, search, research, or application state to start fresh (asks before deleting)
argument-hint: "[profile|search|research|applications|documents|all]"
---

# /reset — Reset Workspace State

Adapted from MadsLorentzen/ai-job-search (MIT).

Reset parts of the workspace so the user can start fresh (usually followed by
`/setup`). **This is destructive.** Nothing is changed until the user types
the confirmation word. Follow the steps in order.

---

## Step 0: Choose the scope

Read the scope from `$ARGUMENTS`. If it's missing or not recognized, ask:

> **What would you like to reset?**
> - **`profile`**: clears your data from the skill modules and the LaTeX
>   template contact blocks. The framework (scoring, writing rules, templates'
>   structure) is preserved.
> - **`search`**: deletes the search caches and rank state (`job_scraper/*.json`).
> - **`research`**: deletes the company research cache (`company_research/*.json`).
> - **`applications`**: deletes generated per-application resumes and cover
>   letters (`resume/resume_*.{tex,pdf}`, `cover_letters/cover_*.{tex,pdf}`) and, only if you say so
>   separately, the tracker (`applications/tracker.json`, `tracker.csv`).
> - **`documents`**: deletes your private source files in `documents/`
>   (including the `documents/applications/` archive). `documents/README.md`
>   is kept.
> - **`all`**: everything above.

Wait for the answer. Several scopes can be combined ("search research").

---

## Step 1: Show exactly what will be cleared

Before touching anything, list precisely what each chosen scope affects.

### `profile`
Read each file and say whether it holds personal data or is already blank:
- `01-candidate-profile.md`: **whole file** reset to its blank template
- `02-behavioral-profile.md`: **whole file** reset to its blank template
- `04-job-evaluation.md`: personalized values only (match areas, experience
  domains, career goals, energizing/draining tasks, constraints, any
  work-authorization/location gate values `/setup` filled) restored to their
  `[PLACEHOLDER]` tokens, plus any "Calibration from past applications"
  section removed. Scoring dimensions, weights, bands, the eligibility and
  language gates, and the research-cache section are **preserved**.
- `05-resume-templates.md`: role-type summary templates (including
  *[Used for: <slug>]* items) cleared. Rules and the cutting procedure are preserved.
- `07-interview-prep.md`: ready-made STAR examples and "STAR candidates" stubs
  cleared. Method, question banks, and roleplay guidance are preserved.
- `resume/template.tex`: contact block restored to placeholders
  (`\name{First}{Last}`, `\title{Target Role}`, `\phone[mobile]{+1~(000)~000~0000}`,
  `\email{you@example.com}`, `\social[linkedin]{your-linkedin}`,
  `\social[github]{your-github}`, `\address{City, ST}{}{}`), and any seeded
  experience/education entries replaced with the generic placeholder entries.
- `cover_letters/template.tex`: name/contact line and signature restored to
  placeholders (`First Last`, `City, ST`, `you@example.com`,
  `+1 (000) 000 0000`, or the equivalent tokens the template ships with).
- `.agents/skills/ats-search/companies.json`: listed, deleted **only if the
  user confirms it separately** (it's a personal target list; the example file
  is kept).

Not touched: `03-writing-style.md`, `06-cover-letter-templates.md`,
`08-outreach.md`, `09-web-research.md`, `10-application-forms.md` (framework
rules). If `/setup` wrote user preferences into 03, mention that and offer to
remove only those additions. Note that `CLAUDE.md` holds no personal data in
this repo; if the user added any, point it out.

> This list must stay in step with what `/setup` Step 3 writes. Every place it
> puts candidate data gets cleared here.

### `search`
Glob `job_scraper/*.json` and list the files (`latest-search.json`,
`ats-search.json`, `linkedin-search.json`, `rank_state.json`, …).
`job_scraper/.gitkeep` is kept.

### `research`
Glob `company_research/*.json` and list them (company name + `fetched_date`).
The folder itself is kept.

### `applications`
Glob `resume/resume_*` and `cover_letters/cover_*` and list each generated
application file (`.tex`, `.pdf`, and any leftover `.aux/.log/.out` or
`preview_*.png`). **Exclude** the shared files: `resume/template.tex`,
`resume/resume-<variant>.tex` master variants (hyphen, not underscore),
`cover_letters/template.tex`, `cover_letters/cover.cls` (it matches `cover_*`
only by accident of naming, so name it explicitly as kept), and
`cover_letters/OpenFonts/`. Show the tracker row count from
`bun run tools/tracker.ts list` and ask **separately** whether to delete the
tracker too (default: keep it, since it's the record of what was submitted).

### `documents`
Glob `documents/**/*` and list everything except `documents/README.md`, grouped
by subfolder (including `documents/applications/<slug>/` archives and
`documents/postings/`). If it's already empty, say so and skip confirmation for
this scope.

---

## Step 2: Explicit confirmation

> **This cannot be undone.** Type **`RESET`** (all caps) to confirm, or
> anything else to cancel.

Anything other than exactly `RESET`: "Reset cancelled. Nothing was changed." Then stop.

---

## Step 3: Execute

### `profile`
- **01:** replace the body with a blank template that keeps the file's current
  section headings and any frontmatter block at the top. Every value becomes
  `[TODO: ask user]`, and the opening note that it's filled by `/setup` stays.
- **02:** the same treatment (keep headings and the frontmatter, values → `[TODO]`).
- **04 / 05 / 07:** targeted Edits only, as listed in Step 1. Never rewrite
  these files wholesale.
- **Templates:** Edit the contact/signature lines back to placeholders.
- **companies.json:** `rm -f .agents/skills/ats-search/companies.json` only if
  separately confirmed.

### `search`
```bash
rm -f job_scraper/*.json
```

### `research`
```bash
rm -f company_research/*.json
```

### `applications`
Remove each listed file explicitly. **Never** use a bare `cover_letters/cover*`
glob, because it would match `cover.cls`:
```bash
rm -f resume/resume_<slug>.* resume/preview_<slug>-*.png          # once per listed slug
rm -f cover_letters/cover_<slug>.* cover_letters/preview_<slug>-*.png
# only if separately confirmed:
rm -f applications/tracker.json applications/tracker.csv
```

### `documents`
Delete every file and subfolder in `documents/` except `README.md`, e.g.
```bash
find documents -mindepth 1 ! -name README.md -delete
```
(Check the listing again first if it's unexpectedly large.)

---

## Step 4: Report

```
## Reset complete
### Cleared
<each file/folder actually changed or deleted>
### Unchanged
<already-empty items and intentionally preserved files>
```

Next steps:
- **profile:** "Run `/setup` to rebuild your profile. It will offer to read
  anything in `documents/`."
- **search:** "Run `/scrape` for fresh results."
- **research:** "The next `/apply` or `/interview` will research companies from scratch."
- **applications:** "Generated drafts are gone. [The tracker was kept / deleted.]"
- **documents:** "Add new source files to `documents/` (see its README), then run `/setup`."

Never touch `documents/` unless the `documents` (or `all`) scope was chosen
and confirmed.
