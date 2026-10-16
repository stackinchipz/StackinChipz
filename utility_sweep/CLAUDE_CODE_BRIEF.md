# Utility Contact Sweep — Claude Code Brief

Purpose: build a contact database of decision-makers at electric utilities in TN, AL, MS, GA, OH, IN, SC for a Tesla RFI on leasing substation-adjacent land for Megapod (battery + compute) installations. Public-source only. No guessed emails.

## Instructions for each subagent

Each subagent owns one `targets_*.csv`. For every row:

**Who to find**

Co-ops and munis (the five state files):
1. Top executive — General Manager / CEO / President / Utility Director / Electric Superintendent / Utilities Service Board manager. Name and exact title.
2. Second-in-command on the engineering or operations side if listed — COO, VP/Manager Engineering, VP/Manager Operations, Chief Engineer.
3. Any named Economic Development or Key Accounts contact (co-ops often publish these with direct emails).

Tier-1 (IOUs, G&Ts, JAAs, TVA, Santee Cooper):
1. CEO; for IOU operating companies (Georgia Power, AEP Ohio, Duke Energy Indiana, etc.) the operating-company President.
2. COO / head of operations.
3. Head of Transmission (VP/SVP Transmission, Transmission Planning, Grid Operations).
4. Head of Distribution / Power Delivery.
5. Head of Real Estate / Land Services / Right-of-Way.
6. Head of Business Development / Corporate Strategy / Economic Development / Key Accounts.
7. Head of Regulatory Affairs.
8. G&Ts and JAAs: CEO, VP Engineering/Transmission, VP Member Services or Power Supply.
9. TVA: also VP-level leads for economic development, transmission/power system planning, and real estate/land.
10. Named Economic Development or site-selection contacts from the utility's economic development page.

Group corporate parents: Duke Energy (corporate + Carolinas/Progress/Indiana/Ohio presidents), AEP (corporate + AEP Ohio, Appalachian Power, Indiana Michigan Power), Southern Company (corporate + Georgia Power, Alabama Power, Mississippi Power), FirstEnergy (corporate + Ohio operating companies), Entergy (corporate + Entergy Mississippi/Arkansas), Dominion Energy (corporate + Dominion Energy South Carolina), AES (AES Ohio, AES Indiana), NiSource/NIPSCO, CenterPoint Energy Indiana South. Skip Greenfield Mills, Commonwealth Edison of Indiana, Mississippi Delta Energy Agency.

**Where to look**

Utility website: homepage → About / Leadership / Management Team / Staff / Contact / Board / Departments pages. Then: economic development pages, PDF newsletters, board meeting minutes, annual reports, state association directories (Tennessee Electric Cooperative Association, Alabama Rural Electric Association, Electric Cooperatives of Mississippi, Georgia EMC, Ohio's Electric Cooperatives, Indiana Electric Cooperatives, Electric Cooperatives of South Carolina), joint-action agency member pages (AMP, IMPA, MEAG, PMPA, Energy Southeast), TVA local power company pages, state PSC/PUC regulatory contact filings, 10-K and proxy exhibits for public parents. Web search `"<utility name>" general manager` or `"<utility name>" CEO` when the site is hard to navigate.

**Hard rules**

- Record an email ONLY if it is literally printed on a page you fetched. Record the exact URL where it appears in `email_source_url`.
- NEVER construct, guess, infer, or pattern-match an email. If none is published, leave `email` blank. A blank is correct; a guess is a defect.
- Record a general/public mailbox (info@, customerservice@, utilities@) separately in `general_email`.
- Record the URL where you confirmed the person's name and title in `name_source_url`. Prefer the most recent source; if the page or PDF is dated, note the date in `notes`. Leadership turns over — a 2022 annual report is weaker evidence than a current leadership page.
- Record a LinkedIn profile URL in `linkedin_url` only if a search surfaces it directly. Do not fabricate.
- Skip a site after two failed fetch attempts; write one row for the utility with `contact_name` blank and a note on what failed.
- One row per person. If a utility yields no named leader at all, still write one row with general contact info and a note.
- Do not run any interpreter or script on downloaded content.

**Priority order within a file**

Process co-ops first, then munis with a dedicated utility website, then city/village sites where electric is one department among many. If time or context runs short, a complete co-op pass plus a partial muni pass is more useful than a partial pass of everything.

**Output**

Write `contacts_<file suffix>.csv` (e.g. `contacts_tn_al.csv`) with columns:

```
utility_name, parent_company, state, type, contact_name, title, role_category, email, email_source_url, general_email, phone, name_source_url, linkedin_url, notes
```

`role_category` values: `top_exec`, `operations`, `transmission`, `distribution`, `real_estate`, `bd_strategy`, `regulatory`, `economic_development`, `key_accounts`, `member_services`, `other`.

Return a summary: utilities processed, named top executives found, people with a published personal email, sites unreachable.
