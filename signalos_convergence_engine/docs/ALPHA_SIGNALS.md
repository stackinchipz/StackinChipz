# Alpha Signals — Estimate Revisions, Insider Activity, Squeeze Fuel

Adds an "expert activity" layer that strengthens the Chaikin Power Gauge
**Experts** bucket and powers a **SQUEEZE** options screen.

Modules: `data_sources/expert_data.py`, `data_sources/edgar_insider.py`,
`features/expert_signals.py`.

## Inputs (normalized contract)
| Column | Meaning | Range |
|---|---|---|
| `estimate_revision_net` | net analyst revisions ~90d (up share − down share) | [-1, 1] |
| `insider_net_ratio` | net insider buying ~90d (buy−sell)/(buy+sell) | [-1, 1] |
| `short_interest_pct` | short interest as fraction of float | [0, 1] |
| `days_to_cover` | short interest / avg daily volume | ≥ 0 |

## Scores (`features/expert_signals.py`)
- **revision_score** — estimate-revision momentum (one of the most robust public
  factors; pairs naturally with the capex-productivity thesis — rising capex +
  rising estimates = confirmation).
- **insider_score** — net insider buying (0 ratio → 50 neutral).
- **squeeze_score** — short-interest fuel: `0.6·SI + 0.4·days-to-cover`.

## Integration
- **Power Gauge Experts bucket** blends `0.55·flow + 0.27·revision + 0.18·insider`
  **only when** revision/insider are present — absent, it falls back to the
  options-flow-only value, so prior behavior is unchanged (backward compatible).
- **SQUEEZE screen** fires for a bullish name with `squeeze_score ≥ 60`, real UOA
  and money flow, and a non-bearish gauge — the asymmetric-fuel long setup.

## Providers
| Provider | Source | Notes |
|---|---|---|
| `demo` | synthetic | offline, deterministic |
| `csv` | your vendor | assemble from FMP/Finnhub/Ortex/etc. |
| `edgar_insider` | SEC Form 4 | best-effort net insider ratio; needs sec.gov egress |

`estimate_revision_net` and `short_interest_pct` need a data vendor (EDGAR has no
consensus estimates or short interest); EDGAR supplies only insider activity.

## Use
```python
from signalos.data_sources.expert_data import load_expert_signals
from signalos.pipeline_screen import run_full_screen

experts = load_expert_signals("demo")
signals = run_full_screen(stock_daily, chain, fundamentals=fund, expert_inputs=experts)
```
The demo runner wires this automatically: `python scripts/run_screen.py --demo`.
