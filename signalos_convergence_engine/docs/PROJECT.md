# SignalOS Project File

## Project Name

**SignalOS**

## Mission

Build a personal quantitative trading operating system that detects asymmetric market setups, validates them with data, rejects weak signals, and helps the user make disciplined defined-risk trading decisions.

SignalOS is not a newsletter. It is a research engine, scanner, dashboard, backtester, and trade journal.

## Initial Product Wedge

**Options Convergence Engine**

A scanner that combines:

```text
Unusual Options Activity = conviction
Money Flow / Accumulation = direction
Convergence = conviction + direction
```

The first module detects abnormal options activity, confirms it with stock-side accumulation/distribution, filters for liquidity, and suggests defined-risk option structures.

## Core Design Principle

```text
No confirmation, no trade.
No backtest, no confidence.
No liquidity, no execution.
No journal, no learning.
```

## Current MVP

The repo currently includes:

- Demo data generator
- Daily options convergence scanner
- UOA scoring model
- Chaikin-style money-flow confirmation
- Liquidity/spread scoring
- Trend and relative strength scoring
- Explicit reject-reason engine
- Defined-risk trade-structure suggestions
- Underlying-return backtest harness
- Streamlit dashboard
- CSV outputs

## Intended Workflow

### Daily

1. Pull market data.
2. Run scanner.
3. Review A+ / Tradable / Watchlist / Rejected signals.
4. Open top candidates in thinkorswim.
5. Check option-chain liquidity manually.
6. Place only defined-risk trades.
7. Journal every trade.

### Weekly

1. Review signal outcomes.
2. Compare accepted vs rejected signals.
3. Tune thresholds only after evidence.
4. Add notes to research log.
5. Push improvements to repo.

## Long-Term Product Vision

SignalOS becomes a modular market intelligence system with:

- Options convergence engine
- Episodic pivot scanner
- Parabolic short scanner
- Breakout scanner
- Relative strength leader board
- Earnings surprise engine
- AI infrastructure stock monitor
- Risk engine
- Trade journal
- Backtest lab
- Mobile dashboard
- Alerting layer
- Broker execution layer, manual first

## Non-Negotiables

- Defined-risk options only
- No naked short options
- No auto-trading until strategy is validated
- Every signal must show reject reasons
- Every model must be backtested against alternatives
- Median return matters more than average return
- Slippage and spread sensitivity must be modeled before real capital scale

## User Context

The user is building SignalOS as a personal trading/research operating system. It should support both discretionary and systematic trading. The user is especially interested in options, unusual options activity, money flow, high-volatility setups, AI/energy/infrastructure stocks, and eventually multiple setups such as Episodic Pivots and Parabolic Shorts.

## Current Version

```text
v0.1 — Options Convergence MVP
```

## Next Version

```text
v0.2 — Real data integration + mobile dashboard deployment
```
