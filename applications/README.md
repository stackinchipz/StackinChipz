# applications/

Your application tracker lives here:

- `tracker.json` — source of truth (managed by `tools/tracker.ts` and `/track`).
- `tracker.csv` — spreadsheet export (`bun run tools/tracker.ts export`).

Both are **git-ignored** (personal data). Only this README is committed.

Status vocabulary: `saved`, `drafted` (pre-submission) · `applied`, `screen`,
`interview`, `offer` (open) · `hired`, `rejected`, `no_response`,
`offer_declined`, `withdrawn` (final). Older records using the previous set
still load.
