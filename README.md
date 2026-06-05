# StackinChipz — AI Job Application Framework (US / LinkedIn)

An AI-powered job application system built on **Claude Code**. Fill in your
profile once, then let Claude evaluate job postings, tailor your resume, write
cover letters, and prep you for interviews — tuned for the **US market** with
ATS-friendly templates.

> Inspired by the open-source [`MadsLorentzen/ai-job-search`](https://github.com/MadsLorentzen/ai-job-search)
> (MIT). The tailoring/review engine follows the same proven pattern; the job
> *discovery* layer has been rebuilt for the US using the **Adzuna** API, and
> the templates have been localized to US/ATS resume conventions.

## What it does

| Command | What it does |
|---|---|
| `/setup` | Onboards your profile — from a resume paste, your `documents/` folder, or a guided interview. |
| `/scrape` | Searches US jobs via Adzuna and ranks them by fit. |
| `/apply <url-or-paste>` | Evaluates fit, tailors a resume + cover letter, runs a drafter→reviewer critique loop, compiles PDFs, and verifies layout. Works on a single **LinkedIn** job URL. |
| `/expand` | Enriches your profile by scanning GitHub, portfolios, and course history. |
| `/upskill` | Analyzes skill gaps vs. target jobs and builds a learning plan. |
| `/reset` | Clears generated profile/search state to start fresh. |

## The LinkedIn approach

LinkedIn has no open jobs API and forbids bulk scraping, so this framework:

- **Discovers** US jobs in bulk through the **Adzuna** aggregator (free dev API,
  includes salary data).
- **Applies** to any specific **LinkedIn** posting one at a time: paste the job
  URL into `/apply` and Claude fetches the public posting (or paste the JD text
  directly). No LinkedIn scraping, no account risk.

## Quick start

1. Install prerequisites — see [SETUP.md](SETUP.md).
2. Get free Adzuna API keys at <https://developer.adzuna.com/> and export them:
   ```bash
   export ADZUNA_APP_ID=your_id
   export ADZUNA_APP_KEY=your_key
   ```
3. In Claude Code, run `/setup` to build your profile.
4. Run `/scrape` to find jobs, or `/apply <linkedin-url>` to tailor an application.

## Architecture

```
.claude/commands/                 # Slash-command definitions
.claude/skills/
  job-application-assistant/       # Core engine: profile + evaluation + templates
  upskill/                         # Skill-gap analysis
.agents/skills/us-job-search/      # Adzuna-backed US job search CLI (Bun)
resume/                            # LaTeX resume template (US/ATS, 1 page)
cover_letters/                     # LaTeX cover letter template (1 page)
documents/                         # Drop your source CV/portfolio/refs here
job_scraper/                       # Cached search results
upskill/                           # Generated skill-gap reports
```

## License

MIT — see [LICENSE](LICENSE).
