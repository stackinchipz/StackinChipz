# 06 — Cover Letter Templates

How to write the cover letter. Source: `cover_letters/template.tex` (compiles
with **xelatex**). Output: `cover_letters/cover_letter.tex`.

## Constraints

- **Exactly 1 page** with a visible signature line.
- Follows `03-writing-style.md` (no em-dashes, no clichés, quantified, concrete).
- Addressed to a specific person/team when discoverable (WebSearch); otherwise a
  clean "Dear [Company] Hiring Team".

## Structure

1. **Hook (1–2 sentences)** — something specific about the company or role that
   proves you researched it (a product, value, recent milestone). Not generic
   flattery.
2. **Fit (1–2 short paragraphs)** — connect 2–3 concrete experiences from `01`
   to the posting's stated requirements. Use the keywords from `04`. Show
   results, not duties.
3. **Why them / why now (optional, 1–2 sentences)** — genuine motivation tied
   to the company's mission or trajectory.
4. **Close** — a clear, low-pressure call to action and thanks. Signature line.

## Do / don't

- **Do** make every sentence earn its place; cut anything generic.
- **Do** keep it skimmable — short paragraphs.
- **Don't** restate the whole resume.
- **Don't** claim experience the candidate doesn't have.

## Verification

Compile with `xelatex`, inspect the PDF: 1 page, signature visible, no overflow.
Fix page breaks with `\needspace` / `\enlargethispage` and recompile.
