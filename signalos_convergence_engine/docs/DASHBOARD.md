# Screen Dashboard

Phone-first Streamlit view of the Capital-Compounder screen.

App: `app/screen_dashboard.py` · Data helpers: `src/signalos/reporting/`

## What it shows
1. **Book risk** — positions, open risk, heat %, and net Δ/Γ/Θ/V (from the risk
   engine via `size_screen`).
2. **Setups by screen** — tabs for Compounder Breakout, Destroyer Breakdown,
   Squeeze, Premium Reversion, Flow Convergence.
3. **All candidates** — the full ranked table (convergence, Power Gauge rating,
   capital verdict, IV regime, structure).
4. **Agent proposals** — propose-only cards with thesis + invalidation per name.

## Run
```bash
python scripts/run_screen.py --demo     # produces outputs/screen_signals.csv
streamlit run app/screen_dashboard.py
```

## Design
Rendering is a thin layer over pure, unit-tested helpers in
`reporting/dashboard_data.py` (`screen_overview`, `screen_by_pattern`,
`book_summary`, `proposal_cards`) — so the data logic is testable without a
running Streamlit server, and the same helpers can back a future React UI.

Deployment (Streamlit Cloud / phone) follows the existing
`docs/STREAMLIT_PHONE_DEPLOYMENT.md`.
