---
description: Analyze skill gaps vs. target jobs and build a learning plan
argument-hint: [job-url-or-role]
---

# /upskill

Compare the candidate profile against target roles and produce a learning plan.

Steps:

1. Determine the target: `$ARGUMENTS` (a job URL or role title), or the most
   common requirements across recent `/scrape` results.
2. Extract required skills/keywords from the posting(s).
3. Diff against `01-candidate-profile.md`: classify each required skill as
   **have / partial / gap**.
4. For each gap, recommend concrete, reputable learning resources (courses,
   docs, projects) with a realistic time estimate, prioritized by impact on
   target-role eligibility.
5. Write the report to `upskill/<role-or-date>.md`.
