# Risk Engine

For an aggressive long-premium options book, the signal engine finds *what* to
trade; the risk engine decides *how much* and whether the book can take it at
all. Everything here is **deterministic** — these are guardrails, not model
judgment. That distinction is the only acceptable thing standing between an
agent and a funded account.

Module: `src/signalos/risk/position_sizing.py`

## Position sizing
```
risk_per_trade  = account_size * risk_pct      (A+ uses aplus_risk_per_trade_pct)
max_loss/contract:
    long option   -> mid * 100                 (premium can go to zero)
    debit spread  -> ~debit * 100              (defined risk)
contracts = floor(risk_budget / max_loss_per_contract)
```

## Portfolio heat
Total open risk as a fraction of the account, capped by
`max_portfolio_heat_pct`. Candidates are sized **top-down**: each fill reduces
the headroom the next candidate sees, so the book can't silently stack to 30%
heat across "5 separate trades" that are really one bet.

## Sector caps
Per-sector open risk is capped by `max_sector_heat_pct` so five correlated AI
names don't become one undiversified position wearing five tickers.

## Book-level Greeks
`aggregate_book_greeks()` nets **Δ / Γ / Θ / V** across all sized positions
(deltas signed by call/put). This is the missing view for a premium buyer: ten
long-call signals = one large long-delta, long-vega, **short-theta** book that
bleeds daily — the aggregate tells you before the market does.

## Kill-switch
New entries halt once the day's P&L breaches `daily_drawdown_kill_pct`, and once
`max_positions` is reached. `size_position()` returns the **binding constraint**
(`portfolio-heat cap`, `sector cap (...)`, `max positions reached`,
`daily drawdown kill-switch`) so every truncated size is explainable.

## Config (`config.py`)
| Param | Default | Meaning |
|---|---|---|
| `account_size` | 100,000 | book size |
| `max_risk_per_trade_pct` | 1.00% | risk per standard position |
| `aplus_risk_per_trade_pct` | 1.50% | risk allowed on A+ setups |
| `max_portfolio_heat_pct` | 6.00% | total open-risk cap |
| `max_sector_heat_pct` | 3.00% | per-sector open-risk cap |
| `max_positions` | 12 | concurrent positions |
| `daily_drawdown_kill_pct` | 4.00% | halt new entries past this daily loss |

## Usage
```python
from signalos.pipeline_screen import run_full_screen, size_screen
signals = run_full_screen(stock_daily, option_chain, fundamentals=fund)
sized = size_screen(signals)          # tradable rows with contracts + dollar_risk
print(sized.attrs["book"])            # heat %, open risk, net Greeks, positions
```

## Before an agent gets execution authority
These caps must be enforced **in this layer**, not in the agent's prompt. The
agent proposes; the risk engine sizes and can veto (contracts = 0). Wire it as
the last gate before any order leaves for Robinhood/Tradier.
