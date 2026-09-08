# Databento OPRA — real options tape

The single highest-impact data upgrade in this engine, because it replaces
**hardcoded constants** that currently drive the directional call.

## The problem it fixes

A Tradier chain *snapshot* can't see who initiated a trade, so
`tradier_provider.py` fills in guesses:

| Field | Today (placeholder) | Drives |
|---|---|---|
| `ask_side_ratio` | `0.65 / 0.55 / 0.50` from volume/OI | 15 pts of UOA **and `infer_bias()`** |
| `repeat_flow_score` | constant `0.50` | 10 pts of UOA |
| `avg_contract_volume_20d` | `volume / 2` | the volume-anomaly term |

That's 25% of the UOA score — and, critically, **`infer_bias()` decides
Bullish vs Bearish from `ask_side_ratio >= 0.55`.** With placeholders, the
directional call is a function of volume/OI, not of who actually paid up.

## What Databento gives us

OPRA (`OPRA.PILLAR`) is the consolidated tape across all 17 US options
exchanges. Using the **`tbbo`** schema — every trade paired with the prevailing
NBBO just before it — we compute, for real:

- **`ask_side_ratio`** — Lee-Ready quote rule per print (at/above ask =
  buyer-initiated, at/below bid = seller-initiated, else vs midpoint), then
  **premium-weighted** so one $2M sweep outweighs a hundred odd-lots.
- **`repeat_flow_score`** — persistence: distinct active minutes + distinct
  prints. Sustained accumulation scores high; one-and-done scores low.
- **`sweep_score`** *(new)* — share of ask-side premium executed in multi-venue
  bursts (same contract, ≥3 exchanges inside 500ms). The classic urgency
  signature that separates real conviction from a resting order getting filled.
- **`avg_contract_volume_20d`** — true trailing baseline from `ohlcv-1d`.

## Use

```bash
pip install databento
export DATABENTO_API_KEY=db-...        # or put it in .env
python scripts/run_live.py             # auto-enriches when the key is present
python scripts/run_live.py --no-databento   # opt out
```

Programmatically:
```python
from signalos.data_sources.databento_provider import (
    DatabentoOptionsProvider, compute_flow_features, enrich_option_chain)

dbp = DatabentoOptionsProvider(api_key=KEY)
trades   = dbp.fetch_option_trades(["NVDA", "PLTR"], start="2026-06-01")
flow     = compute_flow_features(trades)          # per-contract real flow
baseline = dbp.fetch_contract_volume_baseline(["NVDA", "PLTR"], start="2026-04-20")
chain    = enrich_option_chain(chain, flow, baseline)
```

## Design notes

- **Graceful degradation.** No key, no package, or an API error → the pipeline
  logs a warning and keeps the Tradier placeholders. Contracts with no tape
  activity keep their existing values, so partial coverage never blanks the
  screen.
- **Symbology.** Parent symbology (`NVDA.OPT`) pulls every contract on an
  underlying in one request.
- **Testability.** All flow math is pure and network-free
  (`tests/test_databento_provider.py`, 12 tests). Only the fetch methods touch
  the network.

## Cost (be aware)

OPRA is **not free** — pay-as-you-go, or a Standard plan (~$199/mo at time of
writing) that bundles historical OPRA trades/CBBO/OHLCV/definitions. EDGAR
fundamentals and Tradier chains remain the zero/low-cost path; Databento is the
upgrade you buy when you want the flow signal to be real.

## Other Databento clients

`databento-python` is what we use. `databento-rs` (Rust) and the C++ client
expose the same API — relevant only if you later want a low-latency **live**
tape consumer; the historical research path here stays Python.

Sources: [databento-python](https://github.com/databento/databento-python) ·
[OPRA dataset](https://databento.com/datasets/OPRA.PILLAR) ·
[trades schema](https://databento.com/docs/schemas-and-data-formats/trades)
