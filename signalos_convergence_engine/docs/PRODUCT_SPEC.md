# SignalOS Product Specification

## 1. Product Definition

SignalOS is a modular quantitative trading system that converts raw market data into decision-grade trade candidates.

The system should answer:

```text
What is moving?
Why is it moving?
Is the signal confirmed?
Is the trade liquid?
What is the defined-risk structure?
What invalidates the trade?
What happened after similar historical signals?
```

## 2. First Module: Options Convergence Engine

### Inputs

- Daily stock OHLCV
- Options chain
- Options volume
- Open interest
- Bid/ask
- Greeks
- Implied volatility
- Earnings calendar
- Sector / industry map
- Optional: intraday options prints
- Optional: news/catalyst data

### Outputs

- A+ setups
- Tradable setups
- Watchlist setups
- Rejected high-UOA setups
- Ticker drilldown
- Suggested option structure
- Risk rules
- Backtest statistics
- CSV exports

## 3. Core Features

### 3.1 UOA Score

Detects abnormal options activity using:

- Contract volume anomaly
- Premium traded
- Volume/open-interest ratio
- Ask-side buying pressure
- Repeated flow
- Delta quality
- DTE quality
- Spread quality

### 3.2 Money Flow Score

Confirms direction using:

- CMF 5
- CMF 21
- CMF 63
- Close vs 20DMA
- 20DMA vs 50DMA
- Relative strength rank
- Volume expansion

### 3.3 Convergence Score

Weighted model:

```text
35% UOA Score
25% Money Flow Score
15% Trend Score
10% Relative Strength Score
10% Liquidity Score
5% Catalyst Score
```

### 3.4 Reject Reason Engine

Every non-trade needs an explicit reason.

Examples:

```text
Money flow does not confirm direction
Option spread too wide
UOA below threshold
Directional inference unclear
Insufficient open interest
Earnings too close
```

### 3.5 Trade Constructor

Only defined-risk suggestions:

- Long call
- Call debit spread
- Long put
- Put debit spread

No naked options.

## 4. UX Requirements

The dashboard should be phone-friendly.

Pages:

1. Daily Signals
2. Rejected UOA
3. Ticker Drilldown
4. Backtest
5. Trade Journal
6. Settings / Thresholds

## 5. Key Metrics

Track:

- Win rate
- Average return
- Median return
- Max drawdown
- Profit factor
- Payoff ratio
- Signal count
- False positives
- Rejected signals that later worked
- Accepted signals that failed
- Slippage sensitivity
- Spread sensitivity

## 6. Future Modules

### Episodic Pivot Engine

Detects:

- Gap up 10%+
- Massive volume
- Earnings/guidance surprise
- Strong revenue/EPS growth
- ORH entry logic

### Parabolic Short Engine

Detects:

- 50%–100%+ move in large caps
- 300%–1000%+ move in small caps
- 3–5+ green days
- Opening range low breaks
- VWAP failure entries

### AI Infrastructure Monitor

Tracks:

- AI data center stocks
- Energy/grid infrastructure
- Compute/cloud names
- Power/cooling/electrical contractors
- GPU cloud
- Bitcoin miner-to-AI conversion plays

## 7. Product Principle

SignalOS should make it harder to take bad trades.
