# 05 — Resume Templates (US / ATS)

> Adapted from MadsLorentzen/ai-job-search (MIT).

<!-- SETUP: Profile-statement templates and section order are personalized by /setup -->

How to produce the tailored resume. Terminology: always **resume**, never "CV".

## Template

- **Source template:** `resume/template.tex` (moderncv, `banking` style,
  `black` color, `letterpaper`, no photo).
- **Output file:** `resume/resume_<company>_<role>.tex` (lowercase, hyphens;
  e.g. `resume_acme_data-analyst.tex`). If the user keeps role-type variants
  (`resume/resume-backend.tex`, `resume/resume-ml.tex`), start from the closest
  one instead of the blank template.
- **Compile with lualatex:**

  ```bash
  cd resume && lualatex -interaction=nonstopmode resume_<company>_<role>.tex
  ```

  Expected: `Output written on resume_<company>_<role>.pdf (1 page, ...)`.
  Any other page count is a failure to fix before showing the user. PDFs and
  aux/log files are git-ignored.

### Template rules to keep when tailoring

The template's header comment lists these; they are explained further below.

- Date fields use a **single ASCII hyphen** (`2021-2024`, `Jan 2023 - Present`).
- No `\vspace` between `\item` entries.
- Escape `& % $ # _` in body text.
- `\needspace` before an individual `\cventry` only, never before `\section`.
- Every contact detail is printed text (the ATS cannot read icons or link
  targets). Delete unused contact lines rather than leaving them empty; an
  empty `\address{}{}{}` fails to compile.
- Keep the `\AtEndPreamble{\hypersetup{...}}` block (moderncv loads hyperref
  itself; a top-level `\usepackage{hyperref}` clashes on older moderncv) and
  `pdfpagemode=UseNone`. Update `pdftitle`/`pdfauthor` with the candidate's
  name.
- Keep `\ifpdftex\usepackage[T1]{fontenc}\fi` (no-op under lualatex; protects
  the text layer if someone compiles with pdflatex).
- A harmless `Font shape TU/qpl/m/n undefined` warning under lualatex is
  expected with the banking style; ignore it.

## US / ATS rules (non-negotiable)

- **Exactly 1 page.** Two pages only for candidates with 10+ years in senior,
  staff, principal, or executive roles, and only after confirming with the
  user. Everything below assumes 1 page; for an approved 2-page resume, double
  the budget and require exactly 2 pages.
- **No** photo, date of birth, age, marital status, nationality, or headshot.
  Do not list a full street address; `City, ST` is enough.
- Work authorization does **not** go on the resume; it belongs in the
  application form (`10-application-forms.md`) and, if helpful, one line of the
  cover letter.
- Reverse-chronological. Single column. No tables, text boxes, or graphics
  carrying content.
- **No references section.** "References available upon request" is outdated
  in the US and wastes a line. Omit it entirely.

## Recommended section order

**Most roles (experienced candidates):**
1. Header (name, target title, City ST, phone, email, LinkedIn, GitHub/portfolio)
2. Summary (2-3 lines)
3. Experience (reverse-chronological)
4. Skills
5. Education
6. Projects / Certifications (only if relevant)

**New grads, career changers, or credential-gated roles** (licensed,
academic, research): move Education (and Projects) above Experience.

Use standard, ATS-recognizable headings: "Summary", "Experience" (or
"Professional Experience"), "Skills", "Education", "Projects",
"Certifications". Avoid creative headings.

## Tailoring procedure

1. Start from `01-candidate-profile.md`. Never invent content. Mark unknowns
   and ask.
2. Pull the **ATS keywords** from the `04-job-evaluation.md` output and mirror
   them where they truthfully apply: titles, tools, methods. ATS matching is
   literal ("PostgreSQL" will not match "Postgres" in every system; use the
   posting's form).
3. Reorder and emphasize: most role-relevant experience and bullets first;
   demote or drop unrelated content.
4. Rewrite bullets per `03-writing-style.md`: action verb + what + quantified
   result.
5. Tailoring is emphasis and framing, never fabrication. Apply the interview
   backtrack test (`03` rule 6) to every line and flag stretches to the user.

## Section-by-section guidance

### Summary (profile statement)

The most important section to customize. It sits right after `\makecvtitle`.

- **2-3 lines** on a 1-page resume: who the candidate is for *this* role,
  the 2-3 strengths the posting asks for, and the value the employer gets.
- When the role is outside the candidate's home domain, **lead with the
  domain-transfer argument**: the one sentence connecting their background to
  the employer's problem. It is a career-changer's strongest card; play it
  first.
- Use the posting's exact core term (the role's main skill or title) when it
  is true.
- First thing to trim on overflow if it only restates the Skills section.

Keep 2-3 reusable templates for the candidate's main role types, filled by
`/setup`:

**For [YOUR_PRIMARY_ROLE_TYPE] roles:**
> [YOUR_PROFILE_STATEMENT_TEMPLATE_1]

**For [YOUR_SECONDARY_ROLE_TYPE] roles:**
> [YOUR_PROFILE_STATEMENT_TEMPLATE_2]

Statements extracted by `/setup` from past applications are **phrasing
references, never fact sources**: every factual claim still comes from
`01-candidate-profile.md`. A past tailored draft does not vouch for its own
accuracy.

### Skills / core competencies

- Group by category with bold labels (`\cvitem{Languages}{...}`,
  `\cvitem{Tools}{...}`, `\cvitem{Practices}{...}`); 3-5 lines total.
- Reorder per posting: the categories and items the posting names go first.
- Use the posting's own term as the label or item when it truthfully applies
  ("MLOps" beats a paraphrase like "ML deployment").
- Only list skills the candidate can discuss in an interview. No proficiency
  bars or star ratings (they are meaningless to an ATS).

### Experience

- Bullets: 3-5 for the most recent role, 2-3 for the previous, 1-2 for older
  roles. Roles older than ~10-15 years can collapse to one line or be dropped.
- Emphasize measurable results ("Reduced report turnaround from 3 days to 4
  hours"; "Model adopted by 3 teams").
- Show title progression at the same employer as separate `\cventry` lines
  (or one entry with the titles and date ranges stated), so promotions are
  visible.

#### Check tenure against visible output

Look at each role the way a stranger will: **date span versus amount of work
shown.** A two-year role represented by one bullet reads as low output,
fairly or not. This bites hardest on career changers, long-cycle work
(hardware, regulated, research, enterprise deployments), and anyone kept on a
single account.

Honest fixes, in order of preference:

1. **Surface more real work.** Ask what else the period contained: secondary
   projects, internal tooling, support or mentoring work that felt too minor.
2. **Make the phases explicit.** "Ramped up on X and supported Y, then owned Z
   through launch" reads as growth; an undifferentiated block reads as
   stagnation.
3. **Name what made the cycle long.** Live-environment data collection,
   validation with domain experts, regulatory review, iterative deployment.

**Never** pad with invented projects, and **never** shorten employment dates
to improve the ratio. Both are discoverable (US background checks verify
dates) and both are worse than the perception problem. If the gap survives,
record a ready two-part answer (what filled the time, what the outcome was) in
the interview prep (`07-interview-prep.md`).

#### Employment gaps

- Gaps are common and rarely disqualifying in the US; do not hide them with
  year-only dates that misrepresent overlap.
- If a gap needs context, state it matter-of-factly in one line (e.g. a
  `\cventry` for "Career break: caregiving" or "Independent study: [topic]")
  or in the cover letter, never with an apology.
- Show continued development where it is real: courses, certifications,
  freelance or open-source work, volunteering.

### Education

- Degree, field, institution, city/state, dates. Abbreviate degrees the
  US way: B.S., B.A., M.S., MBA, Ph.D.
- GPA only if 3.5+ and within ~3 years of graduation. Honors (cum laude, Dean's
  List) and relevant coursework only for early-career candidates.
- Senior candidates: keep education to one line per degree.

#### In-progress qualifications must say so explicitly

A bare closed range like `2024-2026`, read partway through 2026, looks like a
**finished** degree. A summary line saying "currently completing..." does not
fix it; the education entry is where a reader checks the credential, so it
must stand on its own:

```latex
\cventry{2024-2026}{M.S., Field}{University}{City, ST}{}{In progress, expected May 2026.}
```

Any consistent form works: `In progress, expected <Month Year>.` / `Expected
<Month Year>` / a date field of `2024 - Present`. Claiming a credential not
yet held is a factual misstatement that surfaces at the degree verification
step of a background check. The same applies to certifications and courses.

**Check for agreement:** the summary, the education entry, the cover letter,
and any availability or OPT/EAD date must all give the same completion date.

### Projects and certifications

- Include only those relevant to the posting. For career changers and new
  grads, projects can carry as much weight as a job; give them bullets.
- Certifications: name, issuer, year (or "expected Month Year").

### Evidence links

Wherever the resume names a verifiable artifact (a public repo, a deployed
project, a publication, a portfolio piece, a competition result), carry its
link with `\href` and print a readable URL so it survives ATS text extraction
and printing (`\href{https://github.com/user/repo}{github.com/user/repo}`). A
resume whose strongest claims are checkable reads as more credible
everywhere else.

### LaTeX special characters

Postings and profile data are plain text; the resume is LaTeX. Escape these
wherever they land in body text:

| Character | Write | Typical trigger |
|---|---|---|
| `&` | `\&` | company names: AT\&T, Johnson \& Johnson, P\&G |
| `%` | `\%` | quantified results: "cut latency by 40\%" |
| `$` | `\$` | revenue, savings, budgets: "\$2M annual savings" |
| `#` | `\#` | "ranked \#1", C\# |
| `_` | `\_` | file names, code identifiers |
| `~` | `\textasciitilde{}` | URLs, "approximately" tildes |
| `^` | `\textasciicircum{}` | version strings, math |

Failure modes that deserve special care:

- **`%` fails silently.** An unescaped `%` starts a comment: the compile
  succeeds with zero errors and the rest of the line vanishes from the PDF.
  "Cut latency by 40% and saved $2M" renders as "Cut latency by 40", losing the
  actual result. Check every `%` in every bullet before compiling.
- **`&` fails loudly** inside `\cventry` (alignment-tab errors, `Missing }
  inserted`). Escape employer names up front.
- **A bullet beginning with a literal `[`** must be braced (`\item {[text]}`),
  or LaTeX parses it as `\item`'s optional label and renders it clipped off
  the left margin with a clean compile.

## Compile-and-inspect loop (MANDATORY)

Never present a resume you have not compiled and looked at. "Looks fine in the
`.tex`" is not acceptable (`CLAUDE.md`). Iterate until clean:

1. **Compile:** `lualatex -interaction=nonstopmode resume_<company>_<role>.tex`.
   Fix every `!` error in the log.
2. **Page count:** `pdfinfo resume_<company>_<role>.pdf | grep Pages` must
   print `Pages: 1`.
3. **Render and inspect:**
   `pdftoppm -png -r 80 resume_<company>_<role>.pdf resume_<company>_<role>`
   then open each generated PNG with the **Read** tool and look at it.
   Check for: orphaned entries, a near-empty bottom third, overfull lines
   running into the margin, clipped bullets, inconsistent spacing, missing
   text (a silent `%` cut), and that the header shows every contact detail.
4. **Orphans:** a `\cventry` title must never sit alone at the bottom of a
   page with its bullets on the next (relevant for approved 2-page resumes, and
   as a sign of overflow on 1-page ones).
5. **Text layer** (see ATS parseability below).
6. Delete the PNGs (and aux/log files) when done; never commit build
   artifacts.

### Fixing page-break problems

- **Entry title separated from its bullets:** add `\needspace{5\baselineskip}`
  immediately before that `\cventry` (`needspace` is loaded in the template).
  Use it **before individual entries only, never before `\section`**: a
  section-level `\needspace` pushes the whole section to the next page and
  usually *adds* a page.
- **A line or two spills onto page 2:** first try
  `\enlargethispage{2\baselineskip}` near the end of page 1 for a genuine
  near-miss. If more than a couple of lines spill, cut content (below).
- **Significant content on page 2:** cut content. Do **not** shrink the
  geometry below the template's settings, drop the font below 10pt, or squeeze
  `\vspace`; a cramped resume reads worse than a shorter one.
- **Page ends well short (bottom quarter empty):** restore the
  highest-relevance item that was cut. A half-empty page looks unfinished.

### Spacing inside itemize lists

**Never place `\vspace{...}` between `\item` entries.** It creates a paragraph
break that interacts unpredictably with the list's `\itemsep`, so one gap
renders visibly wider than the rest. The template sets uniform list spacing
with `enumitem`; let it work.

```latex
% WRONG: intermittently produces one oversized gap
\begin{itemize}
  \item First bullet.
  \vspace{1pt}
  \item Second bullet.
\end{itemize}

% RIGHT: uniform native spacing
\begin{itemize}
  \item First bullet.
  \item Second bullet.
\end{itemize}
```

A small `\vspace` between a `\section` heading and its first entry, or between
top-level `\cventry` blocks, is fine and renders consistently.

## ATS parseability

Most US employers (Workday, Greenhouse, Lever, iCIMS, Taleo, etc.) parse the
PDF's **text layer**, not the rendered page. A resume can pass visual
inspection and still extract as garbage. After the visual check, dump the text
layer:

```bash
pdftotext -enc UTF-8 resume_<company>_<role>.pdf - | less
```

Always pass `-enc UTF-8` (some builds default to Latin-1 and turn every
non-ASCII character into a replacement character). Check:

- **Contact details as literal text.** The template's fontawesome icons
  extract as glyph names (`MOBILE-ALT`, `Envelope`, `LINKEDIN-IN`); harmless
  noise because the number, email, and handles print beside them. The failure
  mode is a contact detail carried *only* by an icon or a hyperlink's target.
  The email must appear as printed text.
- **No garbled output.** `(cid:NNN)` markers or `�` mean a font lacks a
  Unicode mapping; the ATS sees the same garbage. Not an issue with the stock
  template under lualatex; watch for it with custom fonts.
- **Reading order.** The banking style is single-column, so extraction order
  matches visual order (the date/location column may extract after the bullets;
  that is acceptable). Multi-column or sidebar templates can interleave
  unrelated lines; tell the user they are trading ATS compatibility for looks.
- **Keyword coverage.** Compare the posting's required and preferred terms
  against the extracted text. Prefer the posting's exact term over a synonym
  when truthful. Never add a keyword the profile does not support.

### Date fields must be ASCII ranges (confirmed ATS import failure)

This fails **silently**: a resume that passes every other check can still
lose its dates on import. In a real Workday import, a resume built from a
moderncv template lost the end date of a short contract and failed to import
any education entry, forcing manual re-entry.

1. **`--` in a date field renders as an en-dash (U+2013), not a hyphen.**
   LaTeX ligatures two ASCII hyphens into one en-dash glyph, so `2016--2024`
   reaches the text layer as `2016–2024`. Many parsers split ranges only on an
   ASCII hyphen. Write the date argument with a **single hyphen**:

   ```latex
   \cventry{2016-2024}{Role}{Company}{City, ST}{}{...}          % parses
   \cventry{Jan 2023 - Present}{Role}{Company}{City, ST}{}{...}  % parses
   \cventry{2016--2024}{Role}{Company}{City, ST}{}{...}         % en-dash, may not
   ```

   This applies to **date arguments only**. Keep `--` in prose where it is
   typographically right (a numeric range like `\$80K--\$100K`).
2. **A bare single year gives the parser no end date.** A short contract or
   internship written `\cventry{2019}` imports with no end. Use an explicit
   range, with months for roles under a year (`Jun 2019 - Aug 2019`). Where a
   real range exists, use it even when a single year would be accurate. Do not
   invent a start date you do not have; a lone graduation year is fine.

Mechanical check for cause 1 (prints any year joined to a Unicode dash; no
output means pass):

```bash
pdftotext -enc UTF-8 resume_<company>_<role>.pdf - \
  | LC_ALL=C.UTF-8 grep -nP '\d\s*[\x{2013}\x{2014}]|[\x{2013}\x{2014}]\s*\d'
```

Cause 2 is a read-through check: confirm every experience entry in the
extracted text shows a start **and** an end.

## Page budget (hard 1-page limit)

| Section | Max budget |
|---|---|
| Header | 3-4 lines (name/title, location, contacts) |
| Summary | 2-3 lines |
| Skills | 3-5 category lines |
| Most recent role | 3-5 bullets |
| Previous role | 2-3 bullets |
| Older roles | 1-2 bullets each, or a single line |
| Education | 1-2 entries, 1 line each (plus an in-progress note if needed) |
| Projects / certifications | 0-3 lines, only if relevant |
| References | none |

**If in doubt, cut rather than squeeze.**

## Relevance-weighted cutting (on overflow)

**Cut by signal, not by section.** Do not trim the oldest items blindly; an
older-role bullet that speaks directly to the posting is worth more than a
recent-role bullet that does not. Score every candidate line on:

1. **Relevance** to *this* posting: does it hit a named tool, keyword, or
   stated responsibility?
2. **Uniqueness:** is it the only place this claim appears, or duplicated
   elsewhere (summary vs. skills vs. a bullet)?
3. **Cover-letter dependency:** does the cover letter lean on it? If cutting
   it would force a rewrite of a letter paragraph, it is load-bearing.
   Interviewers read both documents.

Remove the lowest-scoring line first, regardless of section. Recompile and
re-inspect after each round until the PDF is exactly 1 page.

### Practical order of cuts (easiest first)

1. **Redundancy.** An achievement in both the summary/skills and a bullet:
   cut the summary/skills version (the bullet is the stronger evidence).
2. **Summary fluff.** A sentence that restates what Skills or Experience
   already shows.
3. **Low-relevance experience bullets,** wherever they sit.
4. **Low-relevance supporting content:** an unrelated certification, a
   project that doesn't touch the posting's stack, a skills line the posting
   ignores.
5. **Last-resort structural cuts:** collapse the oldest role to one line,
   drop the oldest education detail, merge Projects into Skills.

### Pitfalls

- Do not mechanically cut "the oldest role first" if that role is exactly
  about the skill the posting wants.
- Do not cut the one concrete example the cover letter relies on.
- Do not cut content for a borderline spill of a line or two; try
  `\enlargethispage` first. Reserve cuts for genuine overflow.

## Other languages

US resumes are in English. In the rare case the user needs a resume in another
language, translate **every** heading (Summary, Experience, Skills,
Education, Projects) along with the body; untranslated headings over
translated prose look sloppy.
