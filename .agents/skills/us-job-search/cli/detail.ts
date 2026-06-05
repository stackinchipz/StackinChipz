#!/usr/bin/env bun
// detail.ts — print a single cached job record by id.
//
// Adzuna has no get-by-id endpoint, so this reads the cache written by
// search.ts. For the full job description, WebFetch the record's `url`.
//
// Usage: bun run detail.ts <id>

import { readFile } from "node:fs/promises";
import { cachePath, type SearchCache } from "./lib.ts";

const id = process.argv[2];
if (!id) {
  console.error("Usage: bun run detail.ts <id>");
  process.exit(1);
}

let cache: SearchCache;
try {
  cache = JSON.parse(await readFile(cachePath(), "utf8"));
} catch {
  console.error(
    `No cached results found at ${cachePath()}. Run search.ts first.`
  );
  process.exit(1);
}

const job = cache.results.find((j) => j.id === id);
if (!job) {
  console.error(
    `Job id ${id} not in the latest search cache. Re-run search.ts or check the id.`
  );
  process.exit(1);
}

console.log(JSON.stringify(job, null, 2));
console.log(
  `\nFor the full description, WebFetch:\n  ${job.url}\n(Adzuna search descriptions are truncated.)`
);
