# SignalOS Feature Backlog

## DONE — Capital-Compounder + Risk + IV layer (this build)

- **FUND-001** Unified fundamentals layer (`data_sources/fundamentals.py`) with
  EDGAR + Tradier/Morningstar providers and a demo generator. ✅
- **CAP-001** Capital-efficiency feature: Uniform-ROA-lite, ROIIC, capex
  productivity (`features/capital_efficiency.py`). ✅
- **CAP-002** Capital-efficiency score + verdict
  (Compounder/Quality/Neutral/Capital Destroyer). ✅
- **PG-001** Chaikin Power Gauge (Financials/Earnings/Technicals/Experts). ✅
- **IV-001** IV-regime feature: iv_rank, expected move, skew, regime. ✅
- **RISK-001** Position sizing + portfolio heat + sector caps + book Greeks +
  kill-switch (`risk/position_sizing.py`). ✅
- **SCREEN-001** Special options screens + regime-aware trade suggestions. ✅
- **PIPE-001** `run_full_screen` merges all layers; `run_screen.py` runner. ✅

See `docs/CAPITAL_COMPOUNDER_SCREEN.md` and `docs/RISK_ENGINE.md`.

## P0 — Required Next

### DATA-001: Add real stock data provider

Description:
Add a stock data abstraction that can load OHLCV from CSV first, then Polygon/Alpaca/Tiingo later.

Acceptance:
`python scripts/run_daily_scan.py --stock-daily real_stock_daily.csv --option-chain real_option_chain.csv` works.

### DATA-002: Add real options chain provider

Description:
Normalize real option-chain data into the required schema.

Required fields:
date, ticker, option_symbol, expiration, strike, type, bid, ask, mid, volume, open_interest, avg_contract_volume_20d, implied_volatility, delta, DTE.

### DATA-003: Add DuckDB / Parquet storage

Description:
Move beyond CSVs.

Acceptance:
Raw data stored in `/data/raw`, processed features stored in `/data/processed`.

### BT-001: Add true options P&L backtest

Description:
Use option prices, not only underlying returns.

Acceptance:
Backtest produces option-level P&L with bid/ask and slippage assumptions.

## P1 — High Value

### UI-001: Improve Streamlit mobile layout

Description:
Make the dashboard easier to read on iPhone.

### UI-002: Add ticker drilldown charts

Description:
Chart close, CMF, volume, and signal events.

### RISK-002: Live broker reconciliation

Description:
Reconcile sized positions against actual broker (Tradier/Robinhood) positions;
feed realized day P&L into the kill-switch.

### DATA-004: IV history store for true 52-week IV rank

Description:
Persist daily ATM IV per ticker so `iv_regime` uses a real 52w rank instead of
the cross-sectional fallback.

### CAP-003: Point-in-time fundamentals

Description:
Use EDGAR filing dates to prevent look-ahead in the capital-efficiency backtest.

### REV-001: Analyst estimate-revision factor

Description:
Add EPS/revenue revision momentum (pairs with the capex-productivity thesis).

### INSIDER-001: Insider (Form 4) + short-interest signals

Description:
Pull Form 4 from EDGAR and short interest / days-to-cover for the Experts bucket
and squeeze setups.

### JOURNAL-001: Add trade journal

Description:
Manual trade logging and result tracking.

### ALERT-001: Daily email report

Description:
Send top A+ setups every morning.

## P2 — Strategy Expansion

### EP-001: Episodic Pivot scanner

Description:
Gap + volume + earnings/guidance surprise detector.

### PS-001: Parabolic Short scanner

Description:
Detect extreme multi-day extension and opening range failure.

### INFRA-001: AI infrastructure watchlist

Description:
Dedicated screen for AI data center, energy, grid, GPU cloud, power/cooling names.

## P3 — Advanced

### ML-001: Learn score weights from history

Description:
Use historical labels to calibrate feature weights.

### NLP-001: News/catalyst summarizer

Description:
Summarize catalyst around each signal.

### EXEC-001: Broker execution integration

Description:
Manual approval only at first.

### AGENT-001: SignalOS research agent

Description:
Explains each setup in plain English with thesis, risk, and invalidation.
