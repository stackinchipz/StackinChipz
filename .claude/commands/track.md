---
description: Log and review job applications (the application tracker)
argument-hint: [add|list|update|export ...]
---

# /track

Manage the application tracker in `applications/tracker.json` via
`tools/tracker.ts`.

If `$ARGUMENTS` is empty, show the current board:

```bash
bun run tools/tracker.ts list
```

Otherwise pass the request through. Common operations:

- **Log a new application:**
  ```bash
  bun run tools/tracker.ts add --company "Acme" --role "Senior SWE" \
    --url "<job-url>" --fit 82 --status applied --source linkedin
  ```
- **Update status:**
  ```bash
  bun run tools/tracker.ts update --id 3 --status interview --notes "phone screen 6/12"
  ```
- **Append a dated note / log a follow-up:**
  `bun run tools/tracker.ts update --id 3 --append-note "recruiter replied"` ·
  `bun run tools/tracker.ts update --id 3 --followup`
- **Find an application:** `bun run tools/tracker.ts find --company "Acme" --open`
- **Gone quiet:** `bun run tools/tracker.ts quiet --days 10`
- **Filter:** `bun run tools/tracker.ts list --status interview` (also `--open`, `--final`, `--json`)
- **Export to CSV:** `bun run tools/tracker.ts export`

Behavior notes:
- `/apply` records an entry automatically (`add --upsert --status drafted`)
  with the fit score, deadline, and file paths; move it to `applied` once the
  user actually submits.
- When the user mentions an outcome ("got a screen at Acme", "rejected by X"),
  prefer `/outcome`, which also archives materials and drafts follow-ups.
- Status vocabulary: `saved`, `drafted` (pre-submission) · `applied`, `screen`,
  `interview`, `offer` (open) · `hired`, `rejected`, `no_response`,
  `offer_declined`, `withdrawn` (final).
