# SignalOS Convergence Engine

A local MVP for an options-flow convergence scanner.

The scanner copies the **logic pattern**, not any proprietary code or vendor model:

```text
Unusual Options Activity = conviction
Money Flow = direction
Convergence = conviction + direction
```

It produces:

- A daily ranked options-convergence screen
- Explicit reject reasons
- Money-flow confirmation
- Liquidity filters
- Defined-risk trade-structure suggestions
- A simple underlying-return backtest harness
- A Streamlit dashboard

The MVP runs without API keys using demo data. Real market data can be plugged in later.

---

## Capital-Compounder Screen (fundamental + risk layer)

On top of the flow scanner, SignalOS now merges a **fundamental conviction +
risk** layer that finds companies deploying capex to grow revenue and
profitability, confirms them with adjusted accounting, and sizes the trade:

```text
Chaikin Power Gauge  +  Uniform-Accounting-lite  +  Capex productivity
        (4 buckets)        (Uniform ROA, distortion gap)   (ROIIC, capex/dep)
   →  named options screens  →  IV-regime-aware structures  →  risk-engine sizing
```

```bash
python scripts/make_demo_data.py     # OHLCV + option chain + fundamentals
python scripts/run_screen.py --demo  # full merged screen, offline
```

Fundamentals providers: **SEC EDGAR** (free) and **Tradier/Morningstar** (beta,
uses your Tradier token). See `docs/CAPITAL_COMPOUNDER_SCREEN.md`,
`docs/RISK_ENGINE.md`, and `docs/ROBINHOOD_AGENT_SETUP.md`.

---

## Quick start

```bash
cd signalos_convergence_engine

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python scripts/make_demo_data.py
python scripts/run_daily_scan.py --demo
python scripts/run_backtest.py --signals outputs/daily_signals.csv
streamlit run app/streamlit_app.py
```

---

## Expected outputs

After running the demo:

```text
outputs/daily_signals.csv
outputs/rejected_uoa_signals.csv
outputs/backtest_summary.csv
outputs/backtest_trades.csv
```

---

## Signal logic

A ticker becomes tradable only when:

```text
1. UOA Score >= threshold
2. Money Flow Score >= threshold
3. Liquidity Score >= threshold
4. Trend / relative strength are supportive
5. No hard rejection condition is triggered
```

Default thresholds live in:

```text
src/signalos/config.py
```

---

## Data contracts

### `stock_daily.csv`

Required columns:

```text
date,ticker,open,high,low,close,volume
```

### `option_chain_latest.csv`

Required columns:

```text
date,ticker,option_symbol,expiration,strike,type,bid,ask,mid,last,
volume,open_interest,avg_contract_volume_20d,implied_volatility,
delta,gamma,theta,vega,days_to_expiration,ask_side_ratio,
repeat_flow_score,catalyst_score
```

---

## Real data integration

The easiest MVP path:

1. Use a broker/vendor for daily stock OHLCV.
2. Use Tradier/Polygon/ORATS/Databento for option chain and options prints.
3. Normalize into the two CSV schemas above.
4. Run `scripts/run_daily_scan.py`.

Suggested production stack:

```text
Storage: DuckDB + Parquet
Research: Python + Polars/Pandas
Dashboard: Streamlit first, React later
Options data: Databento OPRA / ORATS / Polygon / Tradier
Execution: Manual first; broker API later
```

---

## Important risk notes

This is research software. It is not investment advice and does not execute trades.

Options can expire worthless. The engine intentionally favors defined-risk structures and rejects signals when liquidity, money flow, or trend confirmation is poor.

Before risking capital, validate the strategy on real historical options data including slippage, bid/ask spread, stale quotes, missed fills, earnings effects, and survivorship bias.


---

## Project Management Files

This repo now includes a durable SignalOS project layer:

```text
docs/PROJECT.md
docs/PRODUCT_SPEC.md
docs/ROADMAP.md
docs/BACKLOG.md
docs/DATA_PROVIDER_PLAN.md
docs/THINKORSWIM_COMPANION.md
docs/DEPLOYMENT.md
docs/GITHUB_SETUP.md
docs/github_project_backlog.csv
prompts/CURSOR_BUILD_PROMPT.md
```

Use `docs/PROJECT.md` as the canonical project file when continuing development in ChatGPT, Cursor, GitHub, or another coding environment.

---

## Mobile App

SignalOS now includes a phone-first Streamlit dashboard:

```bash
streamlit run app/mobile_app.py
```

Use this for iPhone operation. The original dashboard remains at:

```bash
streamlit run app/streamlit_app.py
```

Mobile deployment docs:

```text
docs/IPHONE_QUICKSTART.md
docs/STREAMLIT_PHONE_DEPLOYMENT.md
docs/PHONE_BUILD_FROM_ZERO.md
```
