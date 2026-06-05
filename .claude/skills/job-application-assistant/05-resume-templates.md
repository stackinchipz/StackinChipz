# 05 — Resume Templates (US / ATS)

How to produce the tailored resume. Source template: `resume/template.tex`
(compiles with **lualatex**). Output: `resume/resume.tex`.

## US/ATS rules (non-negotiable)

- **Exactly 1 page** for most candidates (2 only for 10+ yrs senior/principal —
  confirm with the user).
- **No** photo, date of birth, marital status, age, or headshot.
- Reverse-chronological. Single logical column; avoid layouts that break ATS
  parsing.
- Standard section order: Header → Summary (optional) → Experience → Skills →
  Education → (Projects/Certs if relevant).

## Tailoring procedure

1. Start from the candidate profile (`01`) — never invent content.
2. Mirror the posting's **keywords** (from `04` output) where they truthfully
   apply: titles, tools, methodologies. ATS matches literal terms.
3. Reorder/emphasize: put the most role-relevant experience and bullets first;
   demote unrelated content.
4. Rewrite bullets per `03-writing-style.md`: action verb + what + quantified
   result. Drop weak/irrelevant bullets for this specific role.
5. Keep it truthful — tailoring is emphasis and framing, not fabrication.

## Relevance-weighted cutting (on overflow)

When the resume exceeds 1 page, do **not** just trim the oldest items blindly.
Score each line by:

- **Relevance** to this posting (keyword/requirement alignment),
- **Uniqueness** (does it show something no other line shows?),
- **Cover-letter dependency** (is it referenced in the letter?).

Remove the lowest-scoring lines first. Use `\needspace{}` and
`\enlargethispage{}` to fix bad page breaks. Recompile and **inspect the PDF**
until it's exactly 1 page.

## Variants

If the user targets multiple role types, keep variants like
`resume/resume-backend.tex`, `resume/resume-ml.tex`, and start `/apply` from the
closest one.
