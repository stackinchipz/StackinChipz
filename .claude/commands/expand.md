---
description: Enrich the profile by scanning GitHub, portfolios, and course history
---

# /expand

Surface skills and achievements the user forgot to mention.

Steps:

1. From `01-candidate-profile.md`, collect links the user provided (GitHub,
   portfolio site, personal blog, course platforms).
2. For each:
   - **GitHub**: WebFetch the profile and notable repos; infer languages,
     frameworks, notable projects, and contribution patterns.
   - **Portfolio / blog**: WebFetch and extract projects, case studies, skills.
   - **Courses / certs**: capture completed coursework relevant to target roles.
3. Propose additions to `01-candidate-profile.md` (skills) and
   `02-behavioral-profile.md` (project stories). **Confirm with the user before
   writing** — never assert unverified competence.
4. Note gaps worth addressing with `/upskill`.
