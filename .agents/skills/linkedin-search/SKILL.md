# Skill: LinkedIn / Google Jobs Search (SerpApi)

Surfaces **LinkedIn-sourced** job postings (and other boards) via the Google
Jobs engine through **SerpApi**. Google Jobs aggregates LinkedIn listings, so
this is the practical, ToS-safe way to get LinkedIn results in bulk without
scraping LinkedIn directly.

Use this when you specifically want LinkedIn coverage in `/scrape`. For broad
free discovery use `us-job-search` (Adzuna); for curated companies use
`ats-search` (Greenhouse/Lever).

## Requirements

- `bun install` in `cli/` (one-time).
- A **SerpApi** key (paid; free trial available): set `SERPAPI_KEY`.
  Get one at <https://serpapi.com/>.

## Endpoint

```
GET https://serpapi.com/search.json?engine=google_jobs&q=...&location=...&api_key=...
```

## Commands

### `search`

```bash
bun run cli/search.ts "<query>" [--location "City, ST"] [--linkedin-only] \
  [--remote] [--next-page-token <token>]
```

- Queries Google Jobs via SerpApi.
- `--linkedin-only` keeps results whose source (`via`) or apply link is
  LinkedIn, and prefers the LinkedIn apply URL.
- `--remote` keeps results mentioning remote.
- Pagination: the command prints a `next_page_token`; pass it back with
  `--next-page-token` for the next page.
- Writes normalized results to `job_scraper/linkedin-search.json` (same shape as
  the other sources) and prints a compact table.

Normalized fields: `id, title, company, location, posted, url, via,
description`. Google Jobs descriptions are full-length, so no follow-up fetch is
needed.

## How `/scrape` uses this

Run alongside the other sources, merge + dedupe by `(title, company)`, rank with
`04-job-evaluation.md`. To apply to a specific LinkedIn posting, hand its `url`
to `/apply`.

## Notes

- SerpApi is paid; the cache avoids redundant calls.
- Results reflect Google's aggregation, which is broad but not a 1:1 mirror of
  LinkedIn's own search.
