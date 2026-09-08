import pandas as pd


def backtest_underlying_returns(
    signals: pd.DataFrame,
    stock_daily: pd.DataFrame,
    horizon_days: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    stocks = stock_daily.copy()
    stocks["date"] = pd.to_datetime(stocks["date"])
    stocks = stocks.sort_values(["ticker", "date"])

    frames = []
    for ticker, g in stocks.groupby("ticker"):
        g = g.copy()
        g["future_close"] = g["close"].shift(-horizon_days)
        g["forward_return"] = g["future_close"] / g["close"] - 1
        frames.append(g[["date", "ticker", "close", "future_close", "forward_return"]])
    forward = pd.concat(frames, ignore_index=True)

    s = signals.copy()
    s["date"] = pd.to_datetime(s["date"])
    merged = s.merge(forward, on=["date", "ticker"], how="left")

    merged["bias_adjusted_return"] = merged["forward_return"]
    bearish = merged["bias"].eq("Bearish")
    merged.loc[bearish, "bias_adjusted_return"] = -merged.loc[bearish, "forward_return"]

    valid = merged.dropna(subset=["bias_adjusted_return"]).copy()

    if valid.empty:
        summary = pd.DataFrame([{
            "num_trades": 0,
            "win_rate": None,
            "avg_bias_adjusted_return": None,
            "median_bias_adjusted_return": None,
            "avg_convergence_score": None,
        }])
        return valid, summary

    summary = pd.DataFrame([{
        "num_trades": len(valid),
        "win_rate": float((valid["bias_adjusted_return"] > 0).mean()),
        "avg_bias_adjusted_return": float(valid["bias_adjusted_return"].mean()),
        "median_bias_adjusted_return": float(valid["bias_adjusted_return"].median()),
        "avg_convergence_score": float(valid["convergence_score"].mean()),
    }])

    return valid, summary
