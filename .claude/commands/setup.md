---
description: Onboard your professional profile (documents folder, resume paste, or guided interview)
argument-hint: "[--section identity|education|experience|skills|behavioral|goals|search|writing]"
---

# /setup — Profile Onboarding

Adapted from MadsLorentzen/ai-job-search (MIT).

Collect the user's professional information and fill in the profile files so
`/scrape`, `/rank`, `/apply`, `/interview`, and `/reachout` work out of the box.
There are three paths in. Step 0 picks one, and all three end at Step 3 (write
the files) and Step 4 (confirm).

**Never invent facts.** Anything unknown stays as `[TODO: ask user]`. Every
later command treats `01-candidate-profile.md` as the single source of truth,
so an invented line here ends up on a resume.

---

## Step 0: Privacy check, then choose a path

If `$ARGUMENTS` contains `--section <name>`, jump straight to that section of
Path C and update only the files it feeds. Skip the welcome.

Otherwise, **before writing anything**, check where this working copy
publishes. Run `git remote get-url origin` (if it fails, skip silently). If
it's a GitHub remote and `gh` is available, run
`gh repo view <owner/repo> --json visibility,isFork`. If it's **public**, or a
fork, or the visibility can't be determined, warn and wait:

> **Heads-up before we start:** your `origin` (`<owner/repo>`) looks public.
> Setup writes personal data (name, contact details, work history, work
> authorization, pay floor) into **tracked** files under
> `.claude/skills/job-application-assistant/` and the LaTeX templates. Anything
> you commit and push there is visible to anyone. Either keep profile commits
> local, or push to a **private** repository. Continue?

A private origin or no origin needs no warning.

Then scan `documents/` with Glob (`documents/**/*`, ignoring `README.md`) and
count the files. Group them by subfolder if the user has subfolders (`resume/`,
`linkedin/`, `diplomas/`, `references/`, `projects/`, `applications/`);
otherwise group by apparent type (resume, LinkedIn export, transcript,
reference letter, portfolio write-up).

Welcome the user in **one** message and list three paths. Lead with Path A if
`documents/` has files:

> **Welcome to StackinChipz setup.** I'll build your profile so Claude Code can
> evaluate US job postings, tailor ATS-friendly resumes, write cover letters,
> and prep you for interviews.
>
> I see [N files: e.g. "2 resumes, 1 LinkedIn export, 1 reference letter"] in
> `documents/`. Three ways to start:
>
> **A. Read my documents folder** (recommended). I read everything,
> cross-check it for consistency, and build your profile from real sources.
> Safe to re-run as you add more.
>
> **B. Paste a resume.** Paste or @-mention one resume and I'll ask about
> whatever's missing.
>
> **C. Guided interview.** I walk you through it section by section.
>
> Which would you like?

If `documents/` is empty, present A as "drop your resume / LinkedIn PDF export
/ transcripts / reference letters / project write-ups into `documents/`, then
say go" (see `documents/README.md`). If they pick A and it's still empty, say
what to add and stop.

---

## Path A: Documents folder

Read-before-write and idempotent: anything already in the profile is never
proposed again.

### A1. Inventory
List every file found, grouped as above, and say you'll cross-check before
proposing changes.

### A2. Read the current profile files (once, in parallel)
`01-candidate-profile.md`, `02-behavioral-profile.md`, `03-writing-style.md`,
`04-job-evaluation.md`, `05-resume-templates.md`,
`06-cover-letter-templates.md`, `07-interview-prep.md` (all under
`.claude/skills/job-application-assistant/`). Keep them in context and don't
re-read.

### A3. Extract
- **Resumes:** name, contact (email, phone, LinkedIn, GitHub/portfolio),
  city/state, roles (title, company, dates, location, bullets), skills,
  education, certifications, awards, publications, summary.
- **LinkedIn PDF export:** About (behavioral signal), experience, education,
  skills/endorsements, **Languages** (with proficiency), certifications,
  volunteer work, recommendations (full text). If there are several exports,
  use the newest.
- **Transcripts / diplomas:** official degree name, institution, graduation
  date, GPA or honors if shown.
- **Reference letters:** referee name/title/org, specific quotes, competency language.
- **Project write-ups:** name, problem, stack, hard decisions, measurable outcomes.
- **`documents/applications/<slug>/`** (past applications): from
  `job_posting.md` the role type, sector, and level; from `resume.tex` /
  `cover_letter.tex` the framing patterns; from `outcome.md` the status. Skip
  `in_progress` items for calibration.

### A4. Cross-reference
Look for date, title, degree, and employer-name mismatches across sources. If
there are any, list them numbered ("Resume says X, LinkedIn says Y. Which is
correct?") and **wait** for each one to be resolved. Otherwise say "No
cross-reference issues found."

### A5. Build change sets
For each file, sort findings into **additive** (new: a cert, project,
referee, quote, skill) and **conflicting** (disagrees with what's there).
Inference rules:
- **01:** projects as `- **<Name>**: <problem, stack, outcome>`, grounded in the document.
- **02:** themes from LinkedIn About and recommendations go into the existing
  strengths / work-style sections. Label every inferred line
  *[Inferred from <source>, review before relying on this]*. Never overwrite
  an existing assessment.
- **03:** patterns from 2+ past cover letters go under a "Patterns observed in
  past applications" heading. Never change the rules.
- **04:** outcome pairs. Interviews/offers mark a role type or sector as a
  confirmed strong-fit signal; 2+ silent or rejected applications in a pattern
  get noted. Add them under "Calibration from past applications". Never change
  the scoring framework.
- **05:** a summary statement from a past tailored resume can become a
  role-type template labeled *[Used for: <slug>]*, **only after** every factual
  claim in it is checked against 01. Drafts that drifted must not become
  templates.
- **06:** structurally distinct openings/closings from past letters.
- **07:** achievements without a STAR example get **stubs only** (no full
  stories) under "STAR candidates (complete manually)":
  ```markdown
  ### <Achievement>
  **Source:** <resume / LinkedIn / reference, role/company>
  **What happened:** <one sentence>
  **Good for:** <question types>
  - Situation:
  - Task:
  - Action:
  - Result:
  ```

### A6. Confirm
Show all **additive** changes as one checklist grouped by file, then ask
"Apply all? Reply yes, or list the items to skip." Then go through
**conflicts one at a time** (current text vs. proposed, with options
`keep` / `replace` / `manual`). Write nothing before the user answers.

### A7. Write and fill gaps
Apply only the confirmed items with targeted Edits (never rewrite whole files)
and say what changed per file. Documents rarely cover the US job-search
settings, so then ask about anything not already captured:
work authorization and sponsorship, target roles, metros/remote, pay floor,
deal-breakers, languages, and the search configuration (Path C Sections 1, 7,
and 9). Then continue to Step 3.

---

## Path B: Paste a resume

1. Read it and extract everything Path A's resume bullet lists.
2. Show a short summary of what was captured.
3. Ask follow-ups for the gaps: Path C Sections 1 (US fields), 6 (behavioral),
   7 (goals), 8 (references), and 9 (search).
4. Go to Step 3.

---

## Path C: Guided interview

Have a conversation, not a form. One section at a time; optional sections can
be skipped.

### Section 1: Identity and US work logistics
- Full name; city, state; phone, email, LinkedIn, GitHub/portfolio
- **Work authorization:** US citizen / green card / H-1B / TN / OPT or STEM-OPT
  (with end date) / EAD / other. Explain why it matters: `/apply` runs a hard
  eligibility gate against "no sponsorship" and citizenship/clearance
  language, so this needs to be accurate rather than optimistic.
- **Sponsorship:** needs sponsorship now / in the future (e.g. OPT → H-1B) / never
- **Security clearance:** current level, or "eligible / not eligible"
- **Languages** used professionally, with a plain level (native, fluent,
  conversational). This feeds the language gate.
- Current employment status, earliest start date, notice period
- Relocation willingness (and where)

**Never collect** date of birth, age, marital status, photo, or SSN. US
resumes don't use them.

### Section 2: Education
Degree, field, institution, year (GPA only if strong and recent), honors,
relevant coursework, thesis/capstone. Certifications (issuer, year), bootcamps,
online courses.

### Section 3: Experience (most recent first)
Title, company, city/state or remote, start and end month/year, 3–6
**quantified** accomplishments (push gently for numbers: %, $, users, latency,
team size, time saved), and the tools used. Then independent, freelance,
open-source, or side projects.

### Section 4: Skills
Languages/frameworks with honest proficiency, platforms/cloud, data/ML tools,
domain expertise, methodologies.

### Section 5: Publications, patents, talks, awards (optional)

### Section 6: Behavioral profile
If they have a formal assessment (PI, DISC, CliftonStrengths, Myers-Briggs),
summarize the results. Otherwise ask: where do you do your best work, what
drains you, how do you prefer to collaborate, fast vs. deliberate decisions,
communication style. Draft **2–4 STAR stories** from their answers (leadership,
conflict, failure/learning, biggest impact) using only what they told you.

### Section 7: Goals and preferences
Target roles and industries; what excites them; must-haves and deal-breakers
(on-call, travel, industries to avoid, company stage); **pay floor** (base USD,
and total comp if relevant); **metros** (ideal / acceptable / no) and
**remote preference** (remote-US / hybrid N days / onsite); company size and
stage.

### Section 8: References (optional)
Name, title, company, contact, relationship. Store them in 01 only if the user
wants that.

### Section 9: Search configuration (feeds `/scrape` and `/rank`)
- **Function first, then titles:** "What do you want to be doing day to day?"
  Turn that into 3–8 concrete titles (US titles vary a lot: "Data Scientist",
  "ML Engineer", "Applied Scientist", "Analytics Engineer").
- **Adzuna queries:** 3–6 query strings combining title and key skill (e.g.
  `"backend engineer python"`), each paired with a `City, ST` (or blank for
  nationwide plus a remote filter) and a `--salary-min` matching the pay floor.
- **Target companies (optional):** for each one, find its Greenhouse or Lever
  board token (`boards.greenhouse.io/<token>`, `jobs.lever.co/<token>`). With
  the user's OK, write them to `.agents/skills/ats-search/companies.json`
  (copy the shape of `companies.example.json`; the real file is git-ignored).
- **LinkedIn coverage:** say that `linkedin-search` (Google Jobs via SerpApi)
  is optional and needs `SERPAPI_KEY`. Record whether to use it.
- **Suggest adjacent role types** they may not have considered (e.g. strong
  Python + domain depth → Solutions Engineer / Technical Consultant; ML +
  industry → the same skills in adjacent sectors; tech + PM experience →
  Technical Program Manager). Add the ones they accept as a lower-priority tier.

### Section `writing` (only via `--section writing`)
Ask about tone preferences (formal vs. conversational, words they hate) and
add them to `03-writing-style.md` without removing the existing rules.

---

## Step 3: Write the profile files

For Path A, skip any file A7 already filled. Use targeted edits that keep each
file's structure and headings. All of these files are under
`.claude/skills/job-application-assistant/` unless the path says otherwise.

1. **`01-candidate-profile.md`:** identity and contact, **work authorization,
   sponsorship, clearance, languages**, start date and relocation, target roles
   and search config (titles, metros, remote preference, pay floor, Adzuna
   queries, ATS companies, LinkedIn on/off), experience, projects, skills,
   education, certifications, awards, references, links for `/expand`.
   Replace every `[TODO]` you have an answer for; leave the rest as
   `[TODO: ask user]`.
2. **`02-behavioral-profile.md`:** strengths with proof points, work style and
   values, STAR stories, red lines and preferences.
3. **`03-writing-style.md`:** only add user preferences. The US defaults stay.
4. **`04-job-evaluation.md`:** replace every `[PLACEHOLDER]` token (strong /
   moderate / weak skill-match areas, direct / adjacent / entry-level
   experience domains, career goals, energizing and draining tasks,
   life-situation constraints, and any work-authorization or location gate
   fields) with the user's data. **Leave the scoring framework, weights, bands,
   gates, and research-cache section exactly as they are.**
5. **`05-resume-templates.md`:** add 2–3 role-type summary templates grounded
   in 01, and list which resume variants exist.
6. **`resume/template.tex`:** personalize the contact block (`\name`, `\title`,
   `\phone`, `\email`, `\social[linkedin]`, `\social[github]`,
   `\address{City, ST}`) and seed the education and most recent experience
   entries. No photo, no DOB. Check this whatever path ran, because `/apply`
   copies this file for every application, so a placeholder left here reaches
   a real PDF.
7. **`cover_letters/template.tex`:** personalize the name/contact line and the
   signature. Check this whatever path ran too.
8. **`07-interview-prep.md`:** if the module has a section for ready-made STAR
   examples, add 3–4 from the user's real experience (Path A leaves stubs
   instead).
9. **Smoke-test both templates** so a broken personalization shows up now
   rather than mid-`/apply`:
   ```bash
   cd resume        && lualatex -interaction=nonstopmode -halt-on-error template.tex && pdfinfo template.pdf | grep Pages
   cd cover_letters && xelatex  -interaction=nonstopmode -halt-on-error template.tex && pdfinfo template.pdf | grep Pages
   ```
   Render page 1 with `pdftoppm -png -r 80 template.pdf preview` and look at it
   with the Read tool. Then delete `template.{aux,log,out,pdf}` and
   `preview-*.png`. If LaTeX isn't installed, say so and point to `SETUP.md`.

---

## Step 4: Confirm and next steps

> **Setup complete.** Updated:
> - `01-candidate-profile.md`: facts, US work authorization, search config
> - `02-behavioral-profile.md`: strengths, work style, STAR stories
> - `04-job-evaluation.md`: your match areas, goals, and constraints
> - `05-resume-templates.md`: role-type summaries
> - `resume/template.tex`, `cover_letters/template.tex`: your contact block and signature
> - `07-interview-prep.md`: STAR examples [or: N stubs to complete]
> - `.agents/skills/ats-search/companies.json` [if created]
>
> **Still missing:** [list remaining `[TODO]`s, if any]
>
> **Privacy:** these files now contain personal data and most are tracked by
> git. Keep those commits local, or push only to a private repository.
>
> **Try it:** `/scrape` to find jobs → `/rank` to triage them →
> `/apply <url>` on the best one. `/expand` mines GitHub and your portfolio for
> skills you forgot. Re-run `/setup --section search` whenever your targets change.

If Path A left STAR stubs, add: "Fill in the S/T/A/R details for the [N] stubs
in `07-interview-prep.md` before using them in interviews."

---

## Design principles

- Three paths, one set of output files. Step 0 picks the path from what's in `documents/`.
- Path A is read-before-write and idempotent. Conflicts are always shown and decided by the user.
- Inferred behavioral or style lines are labeled so they get a critical review.
- US conventions throughout: resume (not CV); no photo, DOB, age, marital
  status, or SSN; work authorization captured accurately because it drives a
  hard gate.
- `--section <name>` updates one area without redoing the whole profile.
