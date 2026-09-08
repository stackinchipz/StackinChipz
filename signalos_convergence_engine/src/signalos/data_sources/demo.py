from pathlib import Path
import numpy as np
import pandas as pd


TICKERS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "AMZN", "GOOGL",
    "MP", "FCX", "OXY", "XOM", "BMY", "CRTO", "LYFT", "QXO",
    "ALB", "PLTR", "COIN", "IREN"
]


def make_demo_stock_data(seed: int = 7, periods: int = 220) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=periods)
    frames = []

    for ticker in TICKERS:
        base = rng.uniform(20, 500)
        drift = rng.normal(0.0006, 0.0008)
        vol = rng.uniform(0.015, 0.04)
        returns = rng.normal(drift, vol, size=len(dates))

        if ticker in {"NVDA", "MP", "OXY", "PLTR", "IREN"}:
            returns[-90:] += rng.uniform(0.001, 0.004)
        if ticker in {"FCX", "BMY"}:
            returns[-90:] -= rng.uniform(0.001, 0.003)

        close = base * np.cumprod(1 + returns)
        high = close * (1 + rng.uniform(0.003, 0.025, size=len(dates)))
        low = close * (1 - rng.uniform(0.003, 0.025, size=len(dates)))
        open_ = close * (1 + rng.normal(0, 0.008, size=len(dates)))
        volume = rng.integers(1_000_000, 60_000_000, size=len(dates))

        if ticker in {"NVDA", "MP", "OXY", "PLTR"}:
            volume[-90:] = (volume[-90:] * rng.uniform(1.3, 2.2)).astype(int)

        frames.append(pd.DataFrame({
            "date": dates,
            "ticker": ticker,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume
        }))

    return pd.concat(frames, ignore_index=True)


def make_demo_option_chain(stock_daily: pd.DataFrame, seed: int = 11, signal_offset_bdays: int = 30) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Use a historical signal date so the demo backtest has forward data.
    all_dates = sorted(pd.to_datetime(stock_daily["date"]).unique())
    signal_date = pd.Timestamp(all_dates[-signal_offset_bdays])
    snapshot = stock_daily[pd.to_datetime(stock_daily["date"]).eq(signal_date)].copy()

    hot_bullish = {"NVDA", "MP", "OXY", "PLTR", "IREN", "CRTO", "LYFT"}
    hot_bearish = {"FCX", "BMY"}
    rows = []

    for _, row in snapshot.iterrows():
        ticker = row["ticker"]
        spot = float(row["close"])

        for opt_type in ["call", "put"]:
            for dte in [21, 45, 75]:
                expiration = signal_date + pd.tseries.offsets.BDay(dte)
                for m in [-0.10, -0.05, 0.00, 0.05, 0.10]:
                    strike = round(spot * (1 + m), 2)
                    if opt_type == "call":
                        delta = max(0.05, min(0.85, 0.55 - m * 2.0 + rng.normal(0, 0.03)))
                    else:
                        delta = -max(0.05, min(0.85, 0.45 + m * 2.0 + rng.normal(0, 0.03)))

                    base_vol = int(rng.integers(5, 350))
                    oi = int(rng.integers(50, 5000))
                    avg = max(5, int(base_vol * rng.uniform(0.4, 1.3)))
                    iv = rng.uniform(0.25, 0.95)

                    intrinsic = max(0, spot - strike) if opt_type == "call" else max(0, strike - spot)
                    time_value = spot * iv * np.sqrt(dte / 365) * rng.uniform(0.05, 0.18)
                    mid = max(0.05, intrinsic + time_value)
                    spread = mid * rng.uniform(0.03, 0.18)
                    bid = max(0.01, mid - spread / 2)
                    ask = mid + spread / 2

                    ask_side_ratio = rng.uniform(0.35, 0.70)
                    repeat_flow_score = rng.uniform(0.1, 0.7)
                    catalyst_score = rng.uniform(0.2, 0.7)

                    if ticker in hot_bullish and opt_type == "call" and dte in [45, 75] and 0.0 <= m <= 0.10:
                        base_vol *= int(rng.integers(8, 25))
                        avg = max(5, int(avg / rng.uniform(2, 5)))
                        ask_side_ratio = rng.uniform(0.72, 0.95)
                        repeat_flow_score = rng.uniform(0.75, 1.0)
                        catalyst_score = rng.uniform(0.65, 1.0)

                    if ticker in hot_bearish and opt_type == "put" and dte in [21, 45] and -0.10 <= m <= 0.0:
                        base_vol *= int(rng.integers(8, 22))
                        avg = max(5, int(avg / rng.uniform(2, 5)))
                        ask_side_ratio = rng.uniform(0.72, 0.95)
                        repeat_flow_score = rng.uniform(0.75, 1.0)
                        catalyst_score = rng.uniform(0.65, 1.0)

                    option_symbol = f"{ticker}_{expiration.strftime('%Y%m%d')}_{opt_type.upper()}_{strike}"

                    rows.append({
                        "date": signal_date.date().isoformat(),
                        "ticker": ticker,
                        "option_symbol": option_symbol,
                        "expiration": expiration.date().isoformat(),
                        "strike": strike,
                        "type": opt_type,
                        "bid": round(bid, 2),
                        "ask": round(ask, 2),
                        "mid": round(mid, 2),
                        "last": round(mid * rng.uniform(0.98, 1.02), 2),
                        "volume": int(base_vol),
                        "open_interest": int(oi),
                        "avg_contract_volume_20d": int(avg),
                        "implied_volatility": round(iv, 4),
                        "delta": round(delta, 4),
                        "gamma": round(rng.uniform(0.001, 0.08), 4),
                        "theta": round(-rng.uniform(0.001, 0.08), 4),
                        "vega": round(rng.uniform(0.01, 0.30), 4),
                        "days_to_expiration": int(dte),
                        "ask_side_ratio": round(ask_side_ratio, 4),
                        "repeat_flow_score": round(repeat_flow_score, 4),
                        "catalyst_score": round(catalyst_score, 4),
                    })

    return pd.DataFrame(rows)


def write_demo_data(base_path: str | Path) -> None:
    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)
    stocks = make_demo_stock_data()
    options = make_demo_option_chain(stocks)
    stocks.to_csv(base / "stock_daily.csv", index=False)
    options.to_csv(base / "option_chain_latest.csv", index=False)
