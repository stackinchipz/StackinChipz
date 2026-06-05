---
name: upskill
description: >
  Analyze the gap between the candidate profile and target US roles, then build a
  prioritized learning plan. Use when the user asks what to learn to qualify for
  a role, or after /scrape reveals recurring missing requirements.
---

# Upskill

## Method

1. **Pick the target** — a specific posting (URL), a role title, or the most
   common requirements across recent `/scrape` results (read
   `job_scraper/latest-search.json`).
2. **Extract required skills** from the posting(s); separate must-haves from
   nice-to-haves.
3. **Diff against the profile** (`01-candidate-profile.md`): label each skill
   **have / partial / gap**.
4. **Prioritize gaps** by impact on eligibility and effort to close.
5. **Recommend resources** — reputable courses, official docs, and a concrete
   build-something project for each priority gap, with realistic time estimates.
6. **Write the report** to `upskill/<role-or-date>.md`.

## Output shape

```
# Upskill plan — <role / company / date>

## Summary
- Eligibility now: <short read>
- Top 3 gaps to close: ...

## Gap analysis
| Skill | Status | Priority | How to close | Est. time |

## 30 / 60 / 90 day plan
...
```

Be realistic about timelines and honest about which gaps are dealbreakers
versus learnable on the job.
