---
description: Search US jobs via Adzuna and rank them by fit
---

# /scrape

Find US job postings and rank them against the candidate profile.

Steps:

1. Read target queries, locations, salary floor, and remote preference from the
   candidate profile (`01-candidate-profile.md` and the search section set
   during `/setup`). If none exist, ask the user.

2. For each query, run the Adzuna search CLI:
   ```bash
   cd .agents/skills/us-job-search/cli
   bun run search.ts "<query>" --location "<City, ST>" --max-days 14 --sort date
   ```
   Page through results if needed (`--page 2`, etc.). Requires
   `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` env vars — if unset, tell the user to set
   them (see SETUP.md).

3. Merge results across queries; **deduplicate** by `id` and by
   `(title, company)`.

4. Rank each posting by fit using `04-job-evaluation.md` (skills match,
   experience alignment, behavioral fit). For full descriptions, WebFetch the
   record's `url` — Adzuna's cached descriptions are truncated.

5. Present the top matches as a table: fit score, title, company, location,
   salary, `url`. Recommend which to pursue with `/apply <url>`.

Note: This searches the Adzuna aggregator, not LinkedIn directly. To apply to a
specific LinkedIn posting, use `/apply <linkedin-url>`.
