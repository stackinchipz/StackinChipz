---
description: Onboard your professional profile (resume paste, documents folder, or interview)
---

# /setup

Build or update the candidate profile that powers every other command.

Steps:

1. Ask the user which onboarding path they want:
   - **Paste a resume** — they paste their current resume text.
   - **Documents folder** — read everything in `documents/` (resumes, LinkedIn
     export, transcripts, references).
   - **Guided interview** — ask structured questions covering work history,
     skills, education, achievements, and target roles.
   - If the user passes `--section <name>`, only update that section (e.g.
     `search` for target queries/locations, `profile`, `writing`).

2. Populate these files under `.claude/skills/job-application-assistant/`:
   - `01-candidate-profile.md` — factual background (roles, skills, education).
   - `02-behavioral-profile.md` — strengths, work style, values, STAR stories.
   - `03-writing-style.md` — tone preferences (already has US defaults).
   - And record target **search queries + locations** for `/scrape` (US cities,
     remote preferences, salary floor).

3. Apply **US conventions**: resume not CV, no photo/DOB, ATS-friendly.

4. Confirm what was captured and what is still missing. Never invent facts —
   mark unknowns as `[TODO: ask user]`.
