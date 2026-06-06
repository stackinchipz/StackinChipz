# applications/

Your application tracker lives here:

- `tracker.json` — source of truth (managed by `tools/tracker.ts` and `/track`).
- `tracker.csv` — spreadsheet export (`bun run tools/tracker.ts export`).

Both are **git-ignored** (personal data). Only this README is committed.

Status vocabulary (suggested): `saved`, `applied`, `screen`, `interview`,
`offer`, `rejected`, `withdrawn`.
