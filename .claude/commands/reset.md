---
description: Clear generated profile/search state to start fresh
---

# /reset

Clear generated state. **Confirm with the user before deleting anything.**

Ask which scope:

- **Search cache** — delete `job_scraper/*.json`.
- **Generated documents** — delete `resume/resume.tex`, `resume/*.pdf`,
  `cover_letters/cover_letter.tex`, `cover_letters/*.pdf`.
- **Profile** — blank the profile modules under
  `.claude/skills/job-application-assistant/` back to their template state
  (01, 02; leave 03–07 reference modules intact).
- **Everything** — all of the above.

Never touch `documents/` (the user's private source files) unless explicitly
told to.
