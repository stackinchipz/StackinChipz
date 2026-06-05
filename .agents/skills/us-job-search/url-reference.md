# Adzuna API Reference

Docs: <https://developer.adzuna.com/docs/search>

## Endpoint (US search)

```
GET https://api.adzuna.com/v1/api/jobs/us/search/{page}
```

`{page}` is 1-indexed.

### Required query params

| Param | Meaning |
|---|---|
| `app_id` | Your Adzuna App ID |
| `app_key` | Your Adzuna App Key |

### Common optional params

| Param | Meaning | Example |
|---|---|---|
| `what` | Keywords | `senior software engineer` |
| `what_phrase` | Exact phrase match | `machine learning` |
| `where` | Location | `Austin, TX` |
| `distance` | Radius in km from `where` | `40` |
| `results_per_page` | Page size (max 50) | `20` |
| `max_days_old` | Recency filter (days) | `7` |
| `salary_min` | Minimum salary (USD) | `120000` |
| `full_time` | `1` to restrict to full-time | `1` |
| `sort_by` | `relevance`, `date`, or `salary` | `date` |

### Example

```
https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=ID&app_key=KEY&what=software%20engineer&where=Austin%2C%20TX&max_days_old=7&results_per_page=20&sort_by=date
```

## Response shape (fields we use)

```json
{
  "count": 1234,
  "results": [
    {
      "id": "1234567890",
      "title": "Senior Software Engineer",
      "company": { "display_name": "Acme Corp" },
      "location": { "display_name": "Austin, TX", "area": ["US","Texas","Austin"] },
      "created": "2026-06-01T12:00:00Z",
      "redirect_url": "https://www.adzuna.com/land/ad/1234567890?...",
      "salary_min": 130000,
      "salary_max": 160000,
      "contract_time": "full_time",
      "description": "Truncated description text..."
    }
  ]
}
```

## Notes

- There is **no get-by-id endpoint**. `detail <id>` reads from the cached search
  results; full descriptions come from following `redirect_url`.
- Salary values may be estimated/normalized by Adzuna.
- Rate limits apply on the free tier — cache and batch.
