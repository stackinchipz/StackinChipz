# 10 — Application Form Fields

> Adapted from MadsLorentzen/ai-job-search (MIT).

`/apply` produces a resume and a cover letter. Most US applications also need a
**third artifact**: answers typed into the employer's applicant tracking system
(ATS), such as Workday, Greenhouse, Lever, iCIMS, Ashby, SmartRecruiters, or
Taleo. These include screening questions, knockout yes/no questions, salary
fields, voluntary self-identification, and free-text boxes with character limits.

This module governs that third artifact. It is not a document you compile; it
is text and answers the candidate pastes or selects. Only draft it after
`04-job-evaluation.md` has produced a fit score and the user has chosen to apply.

## The rule that governs everything here

**Every answer must be true and already defensible from `01-candidate-profile.md`
and `02-behavioral-profile.md`**, and consistent with the resume (`05`) and
cover letter (`06`) submitted for the same role. Recruiters read form answers
alongside the resume, and many answers are later checked (background checks,
I-9 verification, degree verification). A form field is a place to *select*
from what is true and arrange it for the question, never to introduce new
claims, inflate scope, or tell the system what it "wants to hear".

All accuracy rules from `03-writing-style.md` and `05-resume-templates.md`
apply unchanged. If a required answer isn't in the profile, ask the user; never
guess, and write the answer into `01` once confirmed.

## Knockout and eligibility questions

ATS screens often auto-reject on these. Answer them **exactly and truthfully**
from the work-authorization section of `01`. A false answer can void an offer
or lead to termination later, and the I-9 process verifies authorization anyway.

| Typical question | How to answer |
|---|---|
| "Are you legally authorized to work in the United States?" | Yes/no per `01`. OPT/STEM OPT/EAD holders are authorized for the duration of their document: answer "Yes". |
| "Will you now or in the future require sponsorship for employment visa status (e.g. H-1B)?" | Yes/no per `01`. If on OPT/STEM OPT and will need H-1B later, the truthful answer is usually **"Yes"**. Never answer "No" to pass the filter. |
| "Are you at least 18 years of age?" | Truthful yes/no (this is lawful and common). |
| "Do you have [N] years of experience with [skill]?" | Count from dated roles in `01`; don't round up. If close, answer truthfully and address it in a free-text field if one exists. |
| "Do you have a [degree] or equivalent experience?" | Per `01`; in-progress degrees are "No" unless the form allows "expected". |
| "Can you work onsite in [city] [N] days a week?" / "Are you willing to relocate?" | Per location preferences in `01`. If it conflicts, that was a `04` gate issue; flag it. |
| "Do you hold / can you obtain a security clearance?" / "Are you a US person under ITAR/EAR?" | Per `01`. Many clearance roles require US citizenship; never imply eligibility you don't have. |
| "Have you previously worked for [company]?" / "Are you related to an employee?" | Truthful. |
| "Have you been convicted of a crime?" | Many states and cities have "ban-the-box" laws that bar asking this before an offer. If asked, the user decides; never fabricate. Point them to their state's rules if unsure. |
| "Are you subject to a non-compete or non-solicit agreement?" | Truthful; suggest the user check their agreement if unsure. |

If the candidate is filtered out by a truthful answer, that's the correct
outcome. Note it in `/track` and move on.

## Salary expectation fields

- If the posting lists a range (common under state and city pay-transparency
  laws), anchor inside it, usually toward the upper half if the fit score
  supports it.
- If the field is required and numeric, enter a number at or above the
  candidate's **floor** in `01`, informed by market data from
  `09-web-research.md` (Levels.fyi, Glassdoor, posted ranges for similar roles).
- If free text is allowed, prefer a range: "140,000 to 160,000 base, flexible
  depending on total compensation." State whether it's base or total comp.
- **Never enter $0, $1, or 999999** to dodge the field: some systems use it as a
  filter and recruiters read it as evasive.
- **Salary history:** many states and cities ban employers from asking. If a
  form asks "current salary" and it's optional, it can be skipped. If required
  in a location where the question is unlawful, the user may enter "N/A" or
  their expectation instead; the user decides. Never invent a number.
- Keep the figure consistent with what the candidate will say in the recruiter
  screen (`07-interview-prep.md`).

## Voluntary self-identification (EEO / OFCCP)

US employers (especially federal contractors) collect gender, race/ethnicity,
veteran status, and disability status on voluntary forms (e.g. the OFCCP
CC-305 disability form and VEVRAA veteran questions).

- These are **voluntary and kept separate from hiring decisions by law**.
- **Never fill these in on the candidate's behalf or infer them.** Present the
  options, including "I don't wish to answer" / "Decline to self-identify", and
  let the user choose. Don't store their answers in the profile unless they ask.
- Don't advise "strategic" answers. Answer truthfully or decline.

## Field type: self-introduction / "Why do you want to work here?"

Usually 100–200 words, one paragraph, no formatting.

**Structure that works:**
1. Current status: what the candidate is doing now.
2. The single strongest piece of evidence for this role, with its number.
3. One line of trajectory, if a pivot or specialization is genuinely interesting.
4. What they want next, connected to this employer's verified work (`09`).

**Rules:**
- **Lead with the strongest evidence, not chronology.**
- **One version per role type.** The same history framed for a backend role and
  a data role are different paragraphs; label them and say which goes where.
- **Tie it to this employer in the final sentence.** Generic answers read as such.
- **Count words and state the count.** Portals truncate silently. Supply a
  trimmed variant and name which sentence to cut first.
- No em-dashes, no clichés (`03`).

## Field type: competency / behavioral questions

"Describe a time you..." with a word cap (often 150–300 words). Use a STAR
story from `02-behavioral-profile.md`, compressed: one sentence each for
Situation and Task, most words on Action, a quantified Result. The same story
will likely come up in the interview (`07`), so keep details identical.

## Field type: structured project or work-history entries

Workday and some ATSs make the candidate re-type work history (title, company,
dates, description) even after a resume upload.

- **Copy from the tailored resume, not from memory.** Dates, titles, and
  employers must match exactly; mismatches are a red flag in background checks.
- **Dates:** MM/YYYY as in `01`. For a project entry, use the dates of *that
  project*, which may be narrower than employment dates, but only if the
  candidate knows when it actually started.
- **Role:** the candidate's role on that project; don't upgrade it.
- **Description:** 100–150 words, plus a ~60-word short version: what it did
  and who used it, the hardest problem and how it was solved, the outcome with
  its number.
- **Scope discipline is stricter here than on a resume.** A project entry with
  the candidate's name attached reads as ownership. Where they contributed
  rather than owned, say so.

## Field type: hard character limits

("In 140 characters, why you?", LinkedIn Easy Apply notes, headline fields.)

1. Pick the single most distinctive true thing: a number, an unusual
   combination of backgrounds, or a problem shape that maps onto the employer's work.
2. Draft 4–6 candidates from different angles.
3. **Count characters programmatically. Do not estimate.** Over-limit text is
   cut mid-word.
4. Present all candidates with counts, recommend one, and say why.

## ATS platform quirks

| Platform | Quirks to plan for |
|---|---|
| **Workday** | Requires an account per employer tenant; resume parsing is unreliable, so re-check every auto-filled field (dates, titles, education often mis-parse). Long multi-page flow; the "My Experience" section often needs manual entry. Saves drafts; sessions time out. |
| **Greenhouse** | Single page; resume plus optional cover letter upload or paste. Custom questions at the bottom (often required, easy to miss). Separate voluntary EEO section. LinkedIn profile URL field. |
| **Lever** | Single page; "Additional information" free-text box is effectively a short cover letter (keep it to ~100–150 words or paste a trimmed letter). Parses resume into name/email/phone; verify. |
| **iCIMS / Taleo / SuccessFactors** | Older parsers: upload a simple single-column PDF or DOCX (the `05` template is built for this). Expect re-typing of history and many knockout questions. |
| **Ashby / SmartRecruiters** | Clean single-page forms; custom questions and salary fields are common. |
| **LinkedIn Easy Apply** | Uses the LinkedIn profile plus an uploaded resume; screening questions are often numeric "years of experience" fields. Answer truthfully; keep the profile consistent with the resume. Prefer the employer's own ATS when the same role is there (`09`). |

General:
- Upload the compiled **PDF** resume unless DOCX is required.
- Text boxes strip formatting: paste plain text, use line breaks rather than
  bullets, and re-read after pasting.
- Some forms count characters including spaces and line breaks; measure that way.
- Use the same email, phone, and LinkedIn URL as the resume.
- Screenshot or save a copy of submitted answers; many portals don't let you
  view them later.

## Output format

Save a plain `.txt` file the candidate can copy from, next to the other
material for that employer, one file per employer covering every field it asked for:

- A header naming the employer, role(s), requisition ID, and ATS platform
- Each field, labelled, with word or character counts stated
- Short variants where limits may be tighter than expected
- Knockout answers listed explicitly (with the `01` source for each)
- **`NOTE TO SELF` blocks** for scope reminders and prepared answers to
  questions the content invites, clearly marked *not for pasting*
- A dates quick reference, so date fields stay consistent

After submitting, log it with `/track` (and later `/outcome`). For a referral or
follow-up message, use `/reachout` and `08-outreach.md`.

## Verification before handing it over

- [ ] Every factual claim traces to `01` / `02` and matches the submitted resume and cover letter
- [ ] Work authorization and sponsorship answers match `01` exactly
- [ ] Salary figure at or above the floor, consistent with interview prep
- [ ] EEO / self-ID fields left for the user to choose (decline option shown)
- [ ] Ownership scoped correctly on contributory work
- [ ] Word and character counts measured, not estimated
- [ ] In-progress qualifications described as in progress
- [ ] No em-dashes or clichés; says "resume", never "CV"
- [ ] `NOTE TO SELF` blocks clearly marked as internal
