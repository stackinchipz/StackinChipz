# Options P&L Backtest

Upgrades the underlying-return proxy to an **option-level** P&L simulation, and
A/B-tests whether the fundamental layer actually adds edge.

Module: `src/signalos/backtest/options_pnl.py` · Runner: `scripts/run_options_backtest.py`

## Method (transparent, no scipy)
- **Entry:** buy the signal's contract at the ask (model mid + half the quoted
  spread), priced via Black-Scholes from entry IV.
- **Path:** each forward business day, reprice with BS using the realized
  underlying close, decayed time-to-expiry, and an IV assumption.
- **Exit:** first of target / stop / expiration / horizon, selling at the
  modeled bid. Debit spreads cap payoff and loss via `spread_debit_frac`.
- **Stress:** `iv_shock` applies an additive vol change over the hold (e.g.
  `-0.20` to simulate an earnings IV crush).

## Metrics
win rate · avg & median return · expectancy · profit factor · payoff ratio ·
max drawdown (equal-weight equity curve).

## Strategy A/B
`compare_strategies()` runs the same engine over three nested filters:

| Strategy | Filter |
|---|---|
| Flow-only | Tradable / A+ by UOA + money flow |
| Convergence>=70 | convergence_score ≥ 70 |
| Convergence+Fundamental | + Compounder/Quality (bull) or Capital Destroyer (bear) |

The question it answers: *does requiring fundamental agreement improve win rate,
expectancy and drawdown — and is it worth the lost trade count?*

## Run
```bash
python scripts/run_screen.py --demo
python scripts/run_options_backtest.py --signals outputs/screen_signals.csv
python scripts/run_options_backtest.py --signals outputs/screen_signals.csv --iv-shock -0.15
```

## Honesty about limits
This is a **model backtest**, not a historical-chain replay. It assumes BS
pricing and a simple IV path; it does **not** capture every real fill, stale
quote, or true historical surface. On demo data the numbers only validate the
**machinery** — the demo is synthetic (compounders are constructed to rise) and
samples are tiny. Real conclusions require:
- live data over many signals (statistical power),
- **point-in-time** fundamentals (no look-ahead — BACKLOG CAP-003),
- stored option-chain snapshots for a true replay (BACKLOG DATA-002+),
- slippage/spread sensitivity sweeps.

Treat it as a research instrument, not proof of edge.
