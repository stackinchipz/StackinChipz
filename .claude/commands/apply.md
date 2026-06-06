---
description: Evaluate fit and produce a tailored resume + cover letter for one posting
argument-hint: <job-url-or-pasted-JD>
---

# /apply

Run the full application workflow for a single posting (works on a **LinkedIn**
job URL). Follow the rules in `CLAUDE.md` and the
`job-application-assistant` skill.

Input: `$ARGUMENTS` — a job URL or pasted job-description text.

Steps:

1. **Get the posting.** If `$ARGUMENTS` is a URL, WebFetch it. If it's a
   LinkedIn URL behind an auth wall and the fetch fails, ask the user to paste
   the job description text instead.

2. **Research the company** with WebSearch (mission, products, recent news,
   tech stack, values).

3. **Evaluate fit** using `04-job-evaluation.md`. Present a fit score and an
   honest recommendation **before** drafting. If it's a weak fit, say so.

4. **Tailor the resume** per `05-resume-templates.md` → write to
   `resume/resume.tex`. Emphasize role-relevant experience and keywords from the
   posting. US/ATS: 1 page, no photo/DOB.

5. **Write the cover letter** per `03-writing-style.md` +
   `06-cover-letter-templates.md` → `cover_letters/cover_letter.tex`.

6. **Drafter → reviewer critique.** Spawn a *separate* reviewer agent (fresh
   context via the Agent tool) to research the employer and critique both drafts
   for missed keywords, weak framing, factual drift, and generic language. The
   drafter then revises.

7. **Compile & verify PDFs** (mandatory — inspect the actual PDF):
   ```bash
   cd resume         && lualatex resume.tex
   cd ../cover_letters && xelatex  cover_letter.tex
   ```
   Resume must be exactly **1 page**, cover letter exactly **1 page** with a
   visible signature. On overflow, apply relevance-weighted cutting and
   `\needspace` / `\enlargethispage`, then recompile until correct.

8. **Log it to the tracker:**
   ```bash
   bun run tools/tracker.ts add --company "<company>" --role "<role>" \
     --url "<url>" --fit <score> --status applied --source <adzuna|ats|linkedin>
   ```

9. Summarize what was produced and flag anything the user should review. Offer
   to draft outreach with `/reachout` (recruiter / hiring-manager / referral).
