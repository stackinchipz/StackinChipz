# documents/

Drop your **private source materials** here so `/setup` and `/expand` can build
your profile:

- Existing resume(s) — PDF, DOCX, or text
- LinkedIn data export
- Transcripts / diplomas / certifications
- Reference letters
- Portfolio descriptions

Everything in this folder (except this README) is **git-ignored** so your
personal files are never committed. Nothing here leaves your machine except what
you explicitly send to Claude during a session.

## Application archive

`/apply`, `/outcome`, and `/interview` keep a per-application archive at
`documents/applications/<slug>/` (same slug rule as `/apply`):

- `job_posting.md` — the posting as fetched (verbatim)
- `resume.tex`, `cover_letter.tex` — copies of what was submitted
- `outcome.md` — status history and what was learned
- `followup_*.md`, `interview_prep_*.md` — drafts and prep packs

It is git-ignored along with the rest of this folder.
