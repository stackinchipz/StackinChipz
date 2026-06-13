# SignalOS Data Provider Plan

## Objective

Move from synthetic demo data to real market data.

## Current State

The current MVP uses:

```text
data/demo/stock_daily.csv
data/demo/option_chain_latest.csv
```

## Required Real Data

### Stock OHLCV

Needed fields:

```text
date,ticker,open,high,low,close,volume
```

### Option Chain

Needed fields:

```text
date,ticker,option_symbol,expiration,strike,type,bid,ask,mid,last,
volume,open_interest,avg_contract_volume_20d,implied_volatility,
delta,gamma,theta,vega,days_to_expiration,ask_side_ratio,
repeat_flow_score,catalyst_score
```

Some fields can be estimated at first:

- ask_side_ratio: estimated from prints later; default 0.5 if chain-only
- repeat_flow_score: calculated after multiple snapshots
- catalyst_score: earnings/news calendar score

## Provider Options

### Fastest MVP

Use Tradier or Polygon for options chain and Greeks.

Pros:
- Easier API setup
- Enough for daily scanning
- Good for MVP

Cons:
- Chain snapshots are weaker than real options prints
- Ask-side/bid-side classification may be limited

### Serious Research

Use Databento OPRA or ORATS.

Pros:
- Real options trade/quote data
- Better for institutional-quality UOA detection
- Better backtesting

Cons:
- More expensive
- More engineering complexity

## Recommended Path

### Phase 1

CSV import of downloaded real data.

### Phase 2

Tradier/Polygon API integration.

### Phase 3

Databento/ORATS historical options backtest.

## Data Quality Checks

Before scoring, validate:

- No missing bid/ask
- Ask > bid
- Mid > 0
- Volume >= 0
- Open interest >= 0
- Expiration > signal date
- DTE calculated correctly
- Stock date and option-chain date aligned

## Storage Plan

```text
data/raw/
data/processed/
data/features/
outputs/
```

Eventually:

```text
DuckDB + Parquet
```
