# Skill: US Job Search (Adzuna)

Searches US job postings via the **Adzuna** aggregator API and returns results
in a normalized shape so the `/scrape` ranking logic can rank them by fit.

This replaces the Danish job-portal scrapers from the upstream project. LinkedIn
itself is **not** scraped in bulk (no open API; against ToS). For a specific
LinkedIn posting, use `/apply <linkedin-url>` instead.

## Requirements

- `bun install` in `cli/` (one-time).
- Env vars `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` (free, from
  <https://developer.adzuna.com/>).

## Commands

### `search`

```bash
bun run cli/search.ts "<query>" [--location "City, ST"] [--max-days N] \
  [--page N] [--results-per-page N] [--salary-min N] [--full-time] [--sort relevance|date|salary]
```

- Queries Adzuna `/v1/api/jobs/us/search/{page}`.
- Writes the normalized results to `job_scraper/latest-search.json` (a cache the
  ranking step and `detail` read from).
- Prints a compact table to stdout, and the full JSON path.

Normalized result fields: `id, title, company, location, posted, url,
salary_min, salary_max, contract_time, description`.

### `detail`

```bash
bun run cli/detail.ts <id>
```

Looks up a job by `id` in the cached `job_scraper/latest-search.json` and prints
its full record, including the `url` (Adzuna redirect to the original posting).
For the complete job description, **WebFetch the `url`** — Adzuna's search
descriptions are truncated.

## How `/scrape` uses this

1. Read the user's target queries/locations from the candidate profile.
2. Run `search` for each query, possibly across multiple pages.
3. Deduplicate by `id` and by `(title, company)`.
4. Rank by fit using `04-job-evaluation.md`.
5. Present the top matches with fit scores and `url`s.

## Limitations

- Adzuna aggregates many boards but is not a 1:1 mirror of LinkedIn.
- Search descriptions are truncated; follow `url` for full text.
- Free tier is rate-limited — the cache avoids redundant calls.
