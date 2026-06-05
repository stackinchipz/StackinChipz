# CLAUDE.md — Job Application Assistant Workspace

This repo turns Claude Code into a US-market job application assistant. Read this
file plus the skill modules under `.claude/skills/job-application-assistant/`
before producing any application materials.

## Golden rule: evaluate fit first

Before drafting **anything**, evaluate fit using `04-job-evaluation.md`:
assess skills match, experience alignment, and behavioral/cultural fit, then
give an honest recommendation on whether to apply. Never jump straight to a
resume or cover letter.

## Workflow (the `/apply` loop)

1. **Research** — Fetch the posting (WebFetch the URL; if it's a LinkedIn page
   behind an auth wall, ask the user to paste the JD). Research the company
   with WebSearch.
2. **Evaluate fit** — Score against `04-job-evaluation.md`; present findings.
3. **Tailor resume** — Follow `05-resume-templates.md`. Start from the closest
   existing variant; emphasize role-relevant experience and keywords.
4. **Write cover letter** — Apply `03-writing-style.md` and
   `06-cover-letter-templates.md`.
5. **Drafter → reviewer critique** — Spawn a *separate* reviewer agent (fresh
   context) to research the employer and critique the drafts for missed
   keywords, weak framing, and generic language. The drafter then revises.
6. **Compile & verify PDFs** — see below.

## Verification is mandatory

Every generated resume and cover letter must pass four checks:

1. **Factual accuracy** — Every claim must match the real candidate profile.
   Verify external facts independently; never invent experience.
2. **Targeting** — Address the specific posting's requirements, not generic
   filler.
3. **Consistency** — Tone and formatting align across both documents.
4. **Quality** — Clean LaTeX, no compile errors. When naming the AI tool used,
   name "Claude Code" explicitly.

## PDF compilation requirements

Both documents must compile **and be visually inspected as PDFs** — "looks fine
in the `.tex`" is not acceptable given LaTeX's pagination quirks.

- **Resume**: compile with `lualatex`, target **exactly 1 page** (US norm).
- **Cover letter**: compile with `xelatex`, target **exactly 1 page** with a
  visible signature line.
- Fix overflow with **relevance-weighted cutting**: score each line by relevance
  to the target posting, uniqueness, and cover-letter dependencies, then remove
  the lowest-value lines first. Use `\needspace` / `\enlargethispage` to prevent
  bad page breaks.

## US market conventions

- Say **"resume"**, not "CV".
- **No** photo, date of birth, marital status, or headshot.
- Keep structure ATS-parseable (avoid multi-column trickery that confuses
  parsers).
- Reverse-chronological, quantified bullet points, strong action verbs.
