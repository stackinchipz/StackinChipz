# Capital-Compounder Screen

The fundamental conviction layer that merges **Chaikin-style analytics**,
**Uniform-Accounting-lite**, and a **capex-productivity edge** into the existing
options-flow convergence engine.

> **Thesis:** find companies deploying capex that *actually* increases revenue
> and profitability — on a distortion-adjusted basis — and time the entry with
> options flow and the IV regime. The inverse (capital destroyers) becomes a
> put/credit screen.

## Disclaimer on the accounting model

The "Uniform Accounting" layer here is a **public approximation (UAFRS-lite)** of
the framework popularized by Valens Research / New Constructs. It reconstructs
adjusted economics from raw filings — it is **not** their proprietary model or
data. Likewise the Power Gauge is a **logic-pattern approximation** of Chaikin
Analytics, not their model. Treat outputs as research, not vendor parity.

## The three lenses

### 1. Uniform ROA (UAFRS-lite) — `features/capital_efficiency.py`
Removes common GAAP distortions to estimate true economic return on operating
assets:
- **Capitalize R&D** (it's investment, not expense): add back R&D net of
  straight-line amortization over `rd_amortization_years`; add the capitalized
  balance to the asset base.
- **Strip goodwill** from the asset base (acquisition accounting noise).
- **Remove excess cash** (cash above `excess_cash_pct_of_revenue`) — it's not
  operating capital.
- `uniform_roa = uniform_earnings / uniform_assets`
- We also record `gaap_roa` and the **`accounting_distortion`** gap — where the
  two diverge most is where the market is most likely mispricing the business.

### 2. ROIIC — return on incremental invested capital
The core "are *new* dollars earning?" metric:
```
ROIIC = Δ NOPAT / Δ Invested Capital   (over roiic_lookback_years)
Invested Capital = total_equity + total_debt − cash
```
ROIIC above `cost_of_capital` = value creation; below = value destruction.

### 3. Capex productivity
- `capex_to_depreciation` > 1 → growth capex, not just maintenance.
- `incr_rev_per_capex` → revenue created per prior-year dollar of capex (1y lag).
- `op_margin_trend` → are margins expanding *while* investing?
- `reinvestment_rate` = capex / NOPAT → how much profit is plowed back.

### Verdict — `scoring/capital_efficiency_score.py`
| Verdict | Condition | Options posture |
|---|---|---|
| **Compounder** | high & rising Uniform ROA, ROIIC > CoC, capex/dep > 1.1 | long calls / call debit |
| **Quality** | strong Uniform ROA, lighter reinvestment | long/debit on flow |
| **Neutral** | mixed | flow-driven only |
| **Capital Destroyer** | ROIIC < 5%, heavy capex, margins compressing | puts / call credit |

## Chaikin Power Gauge — `scoring/chaikin_power_gauge.py`
Four buckets → Bullish / Neutral / Bearish:
- **Financials** — Uniform ROA, ROIIC, ROA trend
- **Earnings** — revenue CAGR, margin trend, incremental margin
- **Technicals** — existing money-flow + trend + relative-strength scores
- **Experts** — options-flow conviction (ask-side / repeat flow / catalyst) as a
  public stand-in for analyst/insider activity

## IV regime — `features/iv_regime.py`
Per ticker: `atm_iv`, `iv_rank`, `expected_move` (ATM straddle), `skew`, and a
`Low / Normal / High / Extreme` label. This is what makes structure selection
regime-aware instead of always buying premium. Supply `iv_history`
(ticker, date, atm_iv) for a true 52-week IV rank; otherwise a cross-sectional
fallback is used.

## Special options screens — `trade_construction/options_screens.py`
| Screen | Fires when | Structure (regime-aware) |
|---|---|---|
| `COMPOUNDER_BREAKOUT` | bullish gauge + Compounder/Quality + bullish flow | low IV → long call/debit; high IV → put credit |
| `DESTROYER_BREAKDOWN` | bearish gauge + Capital Destroyer + bearish flow | long put/debit; high IV → call credit |
| `PREMIUM_REVERSION` | rich IV (High/Extreme) + flow | defined-risk credit spread |
| `FLOW_CONVERGENCE` | classic UOA + money-flow convergence | debit by regime |

Earnings within `earnings_block_dte` days forces a defined-risk spread (IV-crush
guard) instead of naked long premium.

## How it merges — `pipeline_screen.py`
`run_full_screen()` runs the flow base, joins capital-efficiency + IV regime +
Power Gauge by ticker, **re-scores convergence** (now including
`power_gauge_score` and `capital_efficiency_score` per `config.convergence_weights`),
classifies the named screen, then `size_screen()` applies the risk engine.

## Running it
```bash
python scripts/make_demo_data.py            # writes demo OHLCV + chain + fundamentals
python scripts/run_screen.py --demo         # offline end-to-end

# Live (EDGAR fundamentals — free):
python scripts/run_screen.py \
  --stock-daily data/live/stock_daily.csv \
  --option-chain data/live/option_chain_latest.csv \
  --fundamentals-provider edgar --edgar-ua "SignalOS research you@email.com"

# Live (Tradier / Morningstar fundamentals — uses TRADIER_TOKEN):
python scripts/run_screen.py ... --fundamentals-provider tradier
```

## Data providers — `data_sources/`
| Provider | Module | Notes |
|---|---|---|
| Demo | `fundamentals.make_demo_fundamentals` | offline, deterministic |
| SEC EDGAR | `edgar_provider.py` | free; needs egress to `sec.gov` |
| Tradier/Morningstar | `tradier_fundamentals.py` | beta; uses existing Tradier token; also earnings calendar |

All emit the same normalized fundamentals contract, so the screen is
provider-agnostic.
