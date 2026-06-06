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
- **Filter:** `bun run tools/tracker.ts list --status interview`
- **Export to CSV:** `bun run tools/tracker.ts export`

Behavior notes:
- `/apply` should append an entry here automatically (status `applied`) after it
  produces materials, recording the fit score from the evaluation step.
- When the user mentions an outcome ("got a screen at Acme", "rejected by X"),
  update the matching record's status.
- Status vocabulary: saved, applied, screen, interview, offer, rejected,
  withdrawn.
