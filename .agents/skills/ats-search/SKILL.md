# Skill: ATS Search (Greenhouse / Lever)

Pulls job postings **directly from target companies' official ATS feeds** —
Greenhouse and Lever — using their public JSON APIs. No scraping, no API keys,
no ToS risk. This is the highest-quality, most up-to-date signal because it
comes straight from where companies actually post.

Use this alongside `us-job-search` (Adzuna): Adzuna for broad discovery, ATS for
your curated target-company list.

## Requirements

- `bun install` in `cli/` (one-time).
- A company list at `.agents/skills/ats-search/companies.json` (copy
  `companies.example.json` and edit). No credentials needed.

## Public endpoints used

- **Greenhouse:** `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`
- **Lever:** `https://api.lever.co/v0/postings/{token}?mode=json`

The `{token}` is the company's board slug — visible in their careers-page URL
(e.g. `boards.greenhouse.io/stripe` → token `stripe`;
`jobs.lever.co/netflix` → token `netflix`).

## Commands

### `search`

```bash
bun run cli/search.ts [--query "<keywords>"] [--location "<substring>"] \
  [--remote] [--companies path/to/companies.json]
```

- Fetches all postings from every company in the config.
- Optional client-side filters: `--query` (matches title), `--location`
  (substring match), `--remote` (location contains "remote").
- Deduplicates, writes normalized results to `job_scraper/ats-search.json`,
  prints a compact table.

Normalized fields match `us-job-search` (`id, title, company, location, posted,
url, description, ...`) so `/scrape` ranking works identically.

## How `/scrape` uses this

Run both sources, merge + dedupe by `(title, company)`, then rank everything
with `04-job-evaluation.md`. ATS results carry **full descriptions** (Greenhouse
`content=true`, Lever `descriptionPlain`), so they need no follow-up fetch.

## Finding board tokens

Search "{company} greenhouse" or "{company} lever", or check the company's
careers page URL. If a company uses neither (Workday, Ashby, SmartRecruiters),
it won't appear here — use Adzuna or single-URL `/apply` for those.
