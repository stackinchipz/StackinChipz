# thinkorswim Companion Plan

## Role of thinkorswim

thinkorswim should be the execution and mobile monitoring layer, not the full SignalOS brain.

```text
SignalOS Python Engine = brain
Streamlit mobile dashboard = cockpit
thinkorswim = execution terminal
thinkScript = lightweight confirmation overlay
```

## Why Not Pure thinkScript?

thinkScript can handle:

- Money-flow confirmation
- Trend filters
- Watchlist columns
- Stock scans
- Basic option open-interest/volume references

thinkScript is weaker for:

- Full-chain UOA ranking
- Premium traded across contracts
- Ask-side/bid-side trade classification
- Repeated flow clustering
- Historical options backtesting
- Slippage modeling
- Portfolio-level scoring

## First thinkScript: Money Flow Confirmation

```thinkscript
# SignalOS Money Flow Confirmation
# Use on daily aggregation

input cmfLength = 21;
input fastCmfLength = 5;
input shortMA = 20;
input longMA = 50;
input bullishThreshold = 0.10;
input bearishThreshold = -0.10;

def range = high - low;

def moneyFlowMultiplier =
    if range == 0 then 0
    else ((close - low) - (high - close)) / range;

def moneyFlowVolume = moneyFlowMultiplier * volume;

def cmf21 = Sum(moneyFlowVolume, cmfLength) / Sum(volume, cmfLength);
def cmf5 = Sum(moneyFlowVolume, fastCmfLength) / Sum(volume, fastCmfLength);

def sma20 = Average(close, shortMA);
def sma50 = Average(close, longMA);

def bullishTrend =
    close > sma20 and
    sma20 > sma50 and
    cmf21 > bullishThreshold and
    cmf5 > cmf21;

def bearishTrend =
    close < sma20 and
    sma20 < sma50 and
    cmf21 < bearishThreshold and
    cmf5 < cmf21;

plot Signal =
    if bullishTrend then 1
    else if bearishTrend then -1
    else 0;

Signal.AssignValueColor(
    if Signal == 1 then Color.GREEN
    else if Signal == -1 then Color.RED
    else Color.GRAY
);

AssignBackgroundColor(
    if Signal == 1 then Color.DARK_GREEN
    else if Signal == -1 then Color.DARK_RED
    else Color.DARK_GRAY
);
```

## Options Hacker Filters

Suggested settings:

```text
Option Volume > 500
Open Interest > 100
Volume / Open Interest > 1.0
Days to Expiration: 14–90
Delta: 0.25–0.70 for calls
Delta: -0.25 to -0.70 for puts
Sizzle Index > 2.0 or 3.0
Bid/ask spread manually checked
```

## Mobile Workflow

1. Open SignalOS dashboard.
2. Review A+ / Tradable names.
3. Open ticker in thinkorswim mobile.
4. Confirm option chain liquidity.
5. Use limit orders only.
6. Log trade in SignalOS.
