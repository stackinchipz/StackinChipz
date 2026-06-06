# Setup

## 1. Prerequisites

| Tool | Why | Install |
|---|---|---|
| **Claude Code** | Runs the whole framework | `npm install -g @anthropic-ai/claude-code` |
| **Bun** | Runs the Adzuna search CLI | <https://bun.sh> |
| **Python 3.10+** | Optional helper scripts | python.org / your package manager |
| **LaTeX** (`lualatex` + `xelatex`) | Compiles resume & cover letter PDFs | TeX Live (Linux/macOS via MacTeX) or MiKTeX (Windows) |

You also need an **Anthropic API key or Claude subscription** for Claude Code.

### LaTeX packages

The templates use `moderncv`, `fontspec`, and `needspace`. With TeX Live:

```bash
tlmgr install moderncv fontspec needspace
```

## 2. Adzuna API keys (job search)

1. Register a free developer account at <https://developer.adzuna.com/>.
2. Create an app to get an **App ID** and **App Key**.
3. Export them (add to your shell profile to persist):

```bash
export ADZUNA_APP_ID=your_app_id
export ADZUNA_APP_KEY=your_app_key
```

The free tier is sufficient for personal job searching (rate-limited; the CLI
caches results to avoid redundant calls).

### Optional: LinkedIn coverage (SerpApi)

To surface LinkedIn-sourced listings in bulk via Google Jobs, get a **SerpApi**
key (paid; free trial) at <https://serpapi.com/> and export it:

```bash
export SERPAPI_KEY=your_serpapi_key
```

This is optional. Without it, the Adzuna and Greenhouse/Lever sources still work,
and you can always apply to a specific LinkedIn posting with `/apply <url>`.

### Optional: target-company ATS list

To pull jobs straight from companies' Greenhouse/Lever boards, copy the example
and add your targets (no keys needed):

```bash
cp .agents/skills/ats-search/companies.example.json \
   .agents/skills/ats-search/companies.json
```

## 3. Install the search CLI

```bash
cd .agents/skills/us-job-search/cli
bun install
```

Smoke-test it:

```bash
bun run search.ts "software engineer" --location "Austin, TX" --max-days 7
```

## 4. Build your profile

In Claude Code, from the repo root:

```
/setup
```

`/setup` populates the profile modules in
`.claude/skills/job-application-assistant/` (candidate profile, behavioral
profile, writing style) from either:

- an existing resume you paste,
- documents you drop into `documents/`, or
- a guided interview.

## 5. Use it

- `/scrape` — find and rank US jobs.
- `/apply <linkedin-url>` — tailor a full application for one posting.
  - If Claude can't fetch the LinkedIn page (auth wall), just paste the job
    description text after the command instead.
- After `/apply`, compile the PDFs:

```bash
cd resume        && lualatex resume.tex
cd ../cover_letters && xelatex  cover_letter.tex
```

## Notes

- **US/ATS conventions** are baked into the templates: 1-page resume, no photo,
  no date of birth, ATS-parseable structure.
- Nothing about your profile leaves your machine except the Adzuna search query
  and whatever you send to Claude.
