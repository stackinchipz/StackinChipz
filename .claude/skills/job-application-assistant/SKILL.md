---
name: job-application-assistant
description: >
  Core engine for evaluating job fit, tailoring US/ATS resumes, drafting cover
  letters with a drafter-reviewer critique loop, and preparing for interviews.
  Use whenever the user wants to evaluate a posting, build application
  materials, or prep for an interview.
---

# Job Application Assistant

This skill orchestrates the application workflow using the numbered reference
modules in this folder. Always read `CLAUDE.md` first; it holds the golden
rules (evaluate fit first, verification is mandatory, US conventions).

## Modules

| File | Purpose |
|---|---|
| `01-candidate-profile.md` | The user's factual background (filled by `/setup`). |
| `02-behavioral-profile.md` | Strengths, values, STAR stories (filled by `/setup`). |
| `03-writing-style.md` | Tone and language rules for all written output. |
| `04-job-evaluation.md` | The fit-scoring framework. |
| `05-resume-templates.md` | How to tailor the LaTeX resume. |
| `06-cover-letter-templates.md` | How to write the cover letter. |
| `07-interview-prep.md` | Interview preparation method. |
| `08-outreach.md` | Networking/outreach message rules and templates. |

## Workflow

1. **Research & evaluate fit** — Fetch the posting (WebFetch the URL; LinkedIn
   pages may need the user to paste the JD). Research the company with
   WebSearch. Score fit with `04-job-evaluation.md`. Present the score and an
   honest recommendation *before* drafting anything.
2. **Tailor the resume** — Per `05-resume-templates.md`, start from the closest
   existing variant and emphasize role-relevant experience/keywords. US/ATS:
   1 page, no photo/DOB.
3. **Write the cover letter** — Apply `03-writing-style.md` and
   `06-cover-letter-templates.md`.
4. **Drafter → reviewer** — Spawn a *separate* reviewer agent (fresh context)
   to research the employer and critique the drafts. The drafter revises.
5. **Compile & verify PDFs** — `lualatex` for the resume (1 page), `xelatex`
   for the cover letter (1 page, visible signature). Visually inspect the PDF;
   never trust the `.tex` alone. On overflow, use relevance-weighted cutting.
6. **Interview prep** (on request) — Use `07-interview-prep.md`.
7. **Log the application** — Append it to the tracker (`/track` /
   `tools/tracker.ts add`) with the fit score and source.
8. **Outreach** (on request) — Draft networking messages via `/reachout` and
   `08-outreach.md`.

## Granular triggers

Users can invoke a single step: "Evaluate this posting", "Write a resume for
[company]", "Prep me for the [role] interview", or ask for strategy
("What roles should I target?"). Always ground answers in modules 01 and 02.
