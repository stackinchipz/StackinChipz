# 06 — Cover Letter Templates and Tailoring Guide

> Adapted from MadsLorentzen/ai-job-search (MIT).

How to write, typeset, and verify the cover letter for a US application. Always
apply `03-writing-style.md` (voice, banned words, no em-dashes) and ground every
claim in `01-candidate-profile.md` / `02-behavioral-profile.md`. Only draft after
`04-job-evaluation.md` has produced a fit score and the user has chosen to apply.

## US norms at a glance

| Rule | Standard |
|------|----------|
| Length | **250–400 words of body text**, hard limit **1 page** including the signature block |
| Paper | US Letter (8.5 x 11 in), PDF export |
| Salutation | Named person if verifiable → "Dear Hiring Manager," fallback |
| Header | Name, city/state (optional), email, phone, LinkedIn. **No** street address required, no photo, DOB, marital status, or headshot |
| Employer address block | Optional in the US; omit it (it costs 4 lines and ATS ignores it) unless the posting asks for a formal letter |
| Closing | "Sincerely," or "Best regards," followed by a **visible** printed-name signature line |
| Engine | `xelatex` (the class uses `fontspec`) |
| Terminology | "resume", never "CV" |

## Template: `cover.cls` (XeLaTeX)

The cover letter uses a custom class (`cover_letters/cover.cls`) with Lato and
Raleway (SIL Open Font License) bundled in `cover_letters/OpenFonts/fonts/`.

- **Starting point:** `cover_letters/template.tex` (placeholder content, US Letter)
- **Output file:** `cover_letters/cover_<slug>.tex`, using the same `<slug>` rule as `/apply` Step 0 and the resume
- **Location matters:** the class loads fonts with a relative `Path = OpenFonts/fonts/...`, so the `.tex` file must live directly in `cover_letters/` and be compiled from that directory. A letter placed in a subfolder will fail with "font not found".

### Compile command

```bash
cd cover_letters && xelatex -interaction=nonstopmode cover_<slug>.tex
```

Expected log line: `Output written on cover_<slug>.pdf (1 page, ...)`.
Any page count other than 1 is a failure that must be fixed before presenting
the letter. Build artifacts (`.pdf`, `.aux`, `.log`, `.out`) are git-ignored;
never commit them.

## Compile-and-inspect loop (MANDATORY)

"Looks fine in the `.tex`" is not acceptable. After drafting, and again after
the reviewer-driven revision:

1. `xelatex -interaction=nonstopmode cover_<slug>.tex` and confirm it succeeded.
2. `pdfinfo cover_<slug>.pdf | grep Pages` → must print `Pages: 1`.
3. `pdftoppm -png -r 80 cover_<slug>.pdf cover_preview` and open the PNG with the Read tool. Check:
   - the signature line (closing + printed name) is fully visible at the bottom
   - no text runs off the page or overlaps the footer
   - bullet text is in the same font (Raleway Medium) as the body paragraphs
   - the date, salutation, and company/role names are correct
4. Iterate until clean. Delete preview PNGs when done.

### Fixing overflow (relevance-weighted cutting)

If the letter spills to a second page, do not shrink the font below 10.5pt or
crush margins. Instead, score each sentence by (a) relevance to the posting's
must-haves, (b) uniqueness (not already said by the resume), and (c) whether
the resume depends on it for context. Cut the lowest-scoring sentences first.
Then, in order:

1. Merge the personal-fit paragraph into the company paragraph.
2. Drop the 4th or 5th bullet.
3. Add `\usepackage{setspace}` and `\setstretch{0.95}` in the preamble.
4. As a last resort, `\enlargethispage{2\baselineskip}` before the closing.

Use `\needspace{5\baselineskip}` before the closing block if a page break ever
separates the sign-off from the last paragraph.

### Known template pitfall: itemize inside `\lettercontent{}`

`\lettercontent{}` appends `\\` to its argument. If the argument ends in
`\end{itemize}`, LaTeX has no line to end and aborts with
`! LaTeX Error: There's no line here to end.` and no PDF.

**Wrong (breaks compile):**
```latex
\lettercontent{Here is how my experience maps:
\begin{itemize}
    \item ...
\end{itemize}}
```

**Correct:** close `\lettercontent{}` before the list and wrap the list in the
matching Raleway-Medium font so typography stays consistent:
```latex
\lettercontent{Here is how my experience maps:}

{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/, BoldFont = Raleway-Bold]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont
\begin{itemize}
    \item ...
\end{itemize}\par}
\vspace{6pt}

\lettercontent{[next paragraph]}
```

The font wrapper is mandatory. Without it, bullets fall back to the body font
(Lato Light) and visibly mismatch the rest of the letter. Keep the
`BoldFont = Raleway-Bold` option too: without it `\textbf{Label:}` has no bold
shape ("Font shape `TU/Raleway-Medium(0)/b/n' undefined") and silently renders
as regular weight.

Likewise, never put a trailing `\\` inside `\closing{}`: the class appends its
own, and a doubled break triggers the same error.

## Document structure

See `cover_letters/template.tex` for the full compilable file. Skeleton:

```latex
\documentclass[letterpaper]{cover}
\usepackage{fancyhdr}
\usepackage{needspace}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\begin{document}
\thispagestyle{empty}

\namesection{}{\Huge{[YOUR NAME]}}{[City, ST] | \href{mailto:[EMAIL]}{[EMAIL]} | [PHONE] | \href{[LINKEDIN_URL]}{LinkedIn}}

\currentdate{\today}
\lettercontent{Dear [Hiring Manager Name or "Hiring Manager"],}
\lettercontent{[Opening: role + hook + strongest connection, 2-3 sentences]}
\lettercontent{[Why this company: verified specific, 2-3 sentences]}
\lettercontent{[Task-solving lead-in sentence:]}
{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/, BoldFont = Raleway-Bold]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont
\begin{itemize}
    \item \textbf{[Label]:} [concrete achievement mapped to a requirement]
\end{itemize}\par}
\vspace{6pt}
\lettercontent{[Personal fit / how you work, 1-2 sentences]}
\lettercontent{[Close: forward-looking call to action]}

\needspace{5\baselineskip}
\closing{Sincerely,}   % US block format: left-aligned
\signature{[YOUR NAME]}
\end{document}
```

### Key commands

| Command | Purpose |
|---------|---------|
| `\namesection{}{Name}{contact line}` | Centered header with name and contact info |
| `\currentdate{date}` | Right-aligned date (`\today` renders US style, e.g. "October 16, 2026") |
| `\lettercontent{text}` | Body paragraph (adds a blank line after) |
| `\companyname{}` / `\companyaddress{}` | Optional employer address block (usually omitted in the US) |
| `\closing{text}` | Closing line, followed by space for a handwritten signature |
| `\signature{name}` | Printed name: the visible signature line |

## Writing the letter

### Forward-looking framing (the core idea)

A cover letter is **not a resume repeated in prose**. The resume proves what
the candidate did; the letter argues what they will do for *this* employer.

- Frame content around **which of the employer's problems the candidate can solve, and how**: methods, tools, and judgment they will bring.
- Use 1–2 brief past results as evidence for those forward claims, not as the point.
- Say what outcome the employer can expect ("cut onboarding time for your new customers" rather than "I have onboarding experience").
- Focus on what the candidate contributes, not what they gain from the job.

### Structure (3–5 short blocks)

1. **Opening (2–3 sentences).** Name the role (and requisition ID if the posting has one), deliver the hook, and connect the candidate's strongest qualification to the role in one sentence.
2. **Why this company (2–3 sentences), placed early.** One or two *verified* specifics (a product, a stated priority, a recent launch, a team's public work) and why they matter to this candidate. Use language from the posting and the company's own site. Never "a company like yours".
3. **Task-solving body + 3–5 bullets.** One lead-in sentence, then bullets that map achievements from `01` to the posting's must-haves. Mirror the posting's keywords from `04` where they truthfully apply. Include at least one example of initiative.
4. **Personal fit (1–2 sentences, optional).** A behavioral strength from `02` tied to how the team works (e.g. async remote team, customer-facing role). Demonstrate, don't assert.
5. **Close (1–2 sentences).** Confident and forward-looking: "I would welcome the chance to discuss how I could help [team] [specific goal]." Then the signature block.

Count the blocks: opening + company + bullets + close is the default four. Add
the personal-fit block only if the others are short.

### Opening hooks that work

Pick the one that is **true and verifiable** for this candidate and employer:

- **Problem match:** "Your posting describes migrating a monolith to event-driven services while keeping 99.9% uptime. I led exactly that migration at [Company], with zero customer-facing incidents."
- **Product connection:** "I have used [Product] daily for two years to [task], so the chance to work on its [area] is a direct line from user to builder."
- **Verified company moment:** "[Company]'s expansion of [program] into [market] this year is the kind of scale-up I have done twice before."
- **Referral (only if real and permitted):** "[Name] on your [team] suggested I apply after we discussed [topic]."
- **Distinctive combination:** "Five years in clinical operations and three in data engineering put me at the intersection your [role] sits on."

Avoid openers that could be pasted into any letter: "I am writing to apply
for...", "I was excited to see...", "Please accept this letter as...". If a
sentence would survive a find-and-replace of the company name, rewrite it.

### Banned clichés and filler

On top of the `03-writing-style.md` list, cut these on sight:

- "I am passionate about...", "I am excited to apply...", "dream job"
- "I believe I would be a great fit", "I am confident that I would be an asset"
- "leverage my skills", "drive results", "results-driven", "synergy", "value-add"
- "hit the ground running", "wear many hats", "think outside the box", "go-getter"
- "team player", "hard-working", "detail-oriented", "self-starter" (show it instead)
- "To Whom It May Concern", "Dear Sir or Madam"
- "Thank you for your time and consideration" as a standalone final paragraph
- Apologetic hedges: "Although I lack...", "I think I could contribute"
- **No em-dashes.** Use commas, periods, or parentheses.

### Salutation (US)

1. A named hiring manager or recruiter you have **verified** (posting, company site, or a LinkedIn profile you found independently): "Dear Ms. Rivera," or "Dear Jordan Rivera," if unsure of honorific.
2. A named team: "Dear [Company] Data Platform Team,"
3. Fallback: **"Dear Hiring Manager,"**

Never guess a name or gender. Never use "To Whom It May Concern".

### Addressing gaps

If `04` flagged a must-have gap the candidate wants to address, handle it in at
most one sentence, framed forward: adjacent experience plus a concrete
learning step already underway (cross-check `/upskill` output). Never apologize,
never claim the skill.

### Length - hard 1-page limit

- **Word budget: 250–400 words of body text** (excluding header, date, and signature). Aim for ~300. Measured with `template.tex`: the default layout (4 paragraphs + 4 bullets + personal-fit block) overflows `cover.cls` at about 355 words, so above ~350 drop a bullet or the personal-fit block; only a 3-paragraph letter with 3 short bullets gets near 400.
- Count programmatically (`detex file.tex | wc -w`, or strip markup and count) rather than estimating.
- When adding company-specific content, trim elsewhere rather than adding net length.

### Bullets

- 3–5 bullets, placed outside `\lettercontent{}` and wrapped in the Raleway font (see pitfall above).
- Start each with a bold label (`\textbf{Label:}`) or a strong action verb.
- Each bullet: concrete, outcome-oriented, with a number where honest.
- A bullet whose text starts with `[` must be braced: `\item {[text]}`. Unbraced, LaTeX reads `[text]` as `\item`'s optional label and it disappears off the left margin.

### LaTeX special characters

Escape these in body text:
- Ampersand `\&` (e.g. "AT\&T", "Johnson \& Johnson"); unescaped, compile fails loudly
- Percent `\%` ("grew revenue 30\%"); unescaped, it fails **silently**, eating the rest of the line as a comment
- Dollar `\$` ("\$2M ARR"), hash `\#`, underscore `\_`
- Tilde `\textasciitilde{}`, caret `\textasciicircum{}`, backslash `\textbackslash{}`

### Naming the AI tool

If the letter mentions AI-assisted work the candidate did, name the tool
specifically (e.g. "Claude Code"), never a vague "AI tools".

## Example (fictional candidate, for structure only)

> Dear Hiring Manager,
>
> Your Senior Data Engineer posting (Req. 4821) asks for someone to rebuild
> Brightline's nightly batch pipelines as streaming jobs without disrupting the
> clinician dashboards that depend on them. I did that at Northwind Health,
> moving 40 pipelines to Kafka and Flink while dashboards stayed live.
>
> Brightline's public commitment to same-day lab results for rural clinics is
> why this role stands out to me. Latency in that setting is a patient-care
> problem, not just an engineering metric, and it is the problem I want to work on.
>
> Here is how I would approach the first year:
> - **Streaming migration:** cut data freshness from 24 hours to 6 minutes at Northwind by staging the cutover per pipeline with automated parity checks.
> - **Reliability:** introduced data contracts and alerting that reduced on-call pages by 60%.
> - **Cost:** right-sized cluster autoscaling, saving $180K a year in compute.
>
> I work best in written, async teams, and I document decisions so the next
> engineer can move faster than I did.
>
> I would welcome the chance to discuss how I could help your team reach
> same-day results across every clinic.
>
> Sincerely,
> Alex Morgan

(~210 words. The company specifics in a real letter must be verified per
`09-web-research.md`; every candidate claim must trace to `01`.)

## Drafter → reviewer

After the first draft, `/apply` spawns a separate reviewer agent (fresh context)
that researches the employer independently per `09-web-research.md` and critiques
the resume and letter together for missed keywords, weak or generic framing,
unverified company claims, and inconsistency with the resume. The drafter
revises, then reruns the compile-and-inspect loop.

## Checklist before finalizing

- [ ] Fit evaluated first (`04`), user chose to apply
- [ ] 250–400 words of body text, measured not estimated
- [ ] Compiles with `xelatex`; `pdfinfo` reports exactly 1 page
- [ ] PNG preview inspected: signature line visible, fonts consistent, nothing clipped
- [ ] No em-dashes, no clichés from the lists above or `03`
- [ ] Every candidate claim traces to `01`/`02`; no invented experience
- [ ] Every company claim verified from a fetched page (`09`), never a search snippet
- [ ] Forward-looking framing: tasks the candidate will solve, not a resume recap
- [ ] "Why this company" uses a specific, verified detail
- [ ] Company name, role title, requisition ID, and date are correct throughout
- [ ] Salutation: verified name or "Dear Hiring Manager,"
- [ ] No photo, DOB, marital status, or full street address
- [ ] Tone and formatting consistent with the tailored resume (`05`)
- [ ] Says "resume", never "CV"

## Submission guidelines

- Submit only what the employer asks for. If the ATS has an optional cover-letter upload, use it for roles scored 60+ in `04`.
- Upload PDF unless the portal demands DOCX; if pasting into a text box, paste plain text and re-check line breaks (see `10-application-forms.md`).
- Name files clearly: `First-Last-Cover-Letter-Company.pdf` and `First-Last-Resume-Company.pdf`.
- Log the application with `/track` after submitting; record responses later with `/outcome`.
- For follow-up or referral messages, use `/reachout` and `08-outreach.md`.
