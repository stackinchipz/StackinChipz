# SignalOS Roadmap

## v0.1 — Current MVP

Status: Complete

- Demo data generator
- Daily scanner
- UOA score
- Money-flow score
- Convergence score
- Liquidity score
- Reject-reason engine
- Trade-structure suggestions
- Streamlit dashboard
- Basic underlying-return backtest

## v0.2 — Capital-Compounder + Risk Engine

Status: Complete (this build)

The fundamental conviction + risk layer that turns the flow scanner into a
sized, structured system.

- Unified fundamentals layer (EDGAR + Tradier/Morningstar + demo)
- Capital efficiency: Uniform-ROA-lite, ROIIC, capex productivity, verdict
- Chaikin Power Gauge (Financials/Earnings/Technicals/Experts)
- IV regime (iv_rank, expected move, skew) → regime-aware structures
- Special options screens: Compounder Breakout, Destroyer Breakdown,
  Premium Reversion, Flow Convergence
- Risk engine: position sizing, portfolio heat, sector caps, book Greeks,
  daily kill-switch
- `run_full_screen` merge pipeline + `scripts/run_screen.py`
- Robinhood agentic setup checklist (`docs/ROBINHOOD_AGENT_SETUP.md`)

Docs: `docs/CAPITAL_COMPOUNDER_SCREEN.md`, `docs/RISK_ENGINE.md`.

### Next within v0.2
- True 52-week IV rank from a persisted IV history store
- Point-in-time fundamentals (EDGAR filing dates) for the backtest
- Estimate-revision + insider (Form 4) signals

## v0.3 — Real Data Integration (price/options)

Priority: Highest

### Goals

Replace demo data with real market data.

### Tasks

- Add stock OHLCV provider
- Add option-chain provider
- Add earnings calendar provider
- Add data-normalization layer
- Store raw and processed data in Parquet / DuckDB
- Add provider config via `.env`
- Add data-quality checks

### Acceptance Criteria

- Run daily scan on real tickers
- Output current A+ / Tradable / Watchlist / Rejected signals
- No hardcoded synthetic data required

## v0.3 — Phone Dashboard Deployment

Priority: High

### Goals

Make SignalOS usable from iPhone.

### Tasks

- Deploy Streamlit app to Streamlit Cloud / Render / Railway
- Add authentication or private access
- Add mobile-friendly layout
- Add one-click CSV download
- Add daily report view
- Add watchlist export

### Acceptance Criteria

- User can open SignalOS from phone
- User can view daily signals
- User can inspect rejection reasons
- User can cross-check in thinkorswim

## v0.4 — Real Options Backtest

Priority: High

### Goals

Move from underlying-return proxy to true options P&L simulation.

### Tasks

- Add historical option-chain snapshots
- Model bid/ask entry and exit
- Model slippage
- Model expiration
- Model IV changes
- Add target/stop logic
- Add spread simulator

### Acceptance Criteria

- Compare UOA-only vs MoneyFlow-only vs Convergence
- Produce win rate, median return, expectancy, drawdown
- Include spread/slippage sensitivity

## v0.5 — Trade Journal

Priority: Medium

### Goals

Create the learning loop.

### Tasks

- Add manual trade entry
- Add thesis field
- Add signal snapshot
- Add entry/exit price
- Add result
- Add mistake taxonomy
- Add monthly review

### Acceptance Criteria

- Every trade can be logged
- System can compare trades taken vs trades skipped

## v0.6 — thinkorswim Companion

Priority: Medium

### Goals

Make SignalOS usable with thinkorswim on mobile.

### Tasks

- Add thinkScript Money Flow column
- Add bullish/bearish confirmation study
- Add scan settings guide
- Add watchlist workflow
- Add manual execution checklist

### Acceptance Criteria

- User can maintain SignalOS watchlist inside thinkorswim
- User can execute trades manually from phone

## v0.7 — Alerting

Priority: Medium

### Goals

Send daily alerts.

### Tasks

- Email daily report
- SMS/push later
- Telegram/Discord optional
- Add threshold-based alerts

### Acceptance Criteria

- User receives daily A+ setup report automatically

## v0.8 — Episodic Pivot Module

Priority: Medium

### Goals

Add EP scanner.

### Tasks

- Gap scanner
- Volume shock scanner
- Earnings surprise parser
- ORH levels
- Stop/position logic
- Backtest

## v0.9 — Parabolic Short Module

Priority: Medium

### Goals

Add parabolic short scanner.

### Tasks

- Multi-day extension detector
- Volume/climax detector
- Opening range low breaks
- VWAP failure detector
- Stop/target system
- Backtest

## v1.0 — SignalOS Research Terminal

Priority: Long Term

### Goals

Unified market dashboard.

### Includes

- Options convergence
- EP
- Parabolic short
- AI infrastructure monitor
- Trade journal
- Risk dashboard
- Mobile alerts
- Backtesting lab
