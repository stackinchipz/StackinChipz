import numpy as np
import pandas as pd


def chaikin_money_flow(df: pd.DataFrame, window: int = 21) -> pd.Series:
    """
    Public approximation of institutional accumulation/distribution.

    Money Flow Multiplier =
    ((Close - Low) - (High - Close)) / (High - Low)

    CMF =
    Sum(Money Flow Volume, N) / Sum(Volume, N)
    """
    required = {"high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for CMF: {missing}")

    high_low_range = (df["high"] - df["low"]).replace(0, np.nan)
    multiplier = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / high_low_range
    money_flow_volume = multiplier.fillna(0) * df["volume"]
    cmf = money_flow_volume.rolling(window).sum() / df["volume"].rolling(window).sum()
    return cmf.replace([np.inf, -np.inf], np.nan).fillna(0)


def add_money_flow_features(stock_daily: pd.DataFrame) -> pd.DataFrame:
    df = stock_daily.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"])

    frames = []
    for ticker, g in df.groupby("ticker", sort=False):
        g = g.copy()
        g["cmf_5"] = chaikin_money_flow(g, 5)
        g["cmf_21"] = chaikin_money_flow(g, 21)
        g["cmf_63"] = chaikin_money_flow(g, 63)
        g["sma_20"] = g["close"].rolling(20).mean()
        g["sma_50"] = g["close"].rolling(50).mean()
        g["return_20d"] = g["close"].pct_change(20)
        g["return_63d"] = g["close"].pct_change(63)
        g["volume_ratio_20d"] = g["volume"] / g["volume"].rolling(20).mean()
        frames.append(g)

    out = pd.concat(frames, ignore_index=True)
    out["rs_rank"] = (
        out.groupby("date")["return_63d"]
        .rank(pct=True)
        .fillna(0.5)
        * 100
    )
    return out


def latest_money_flow_snapshot(stock_daily: pd.DataFrame) -> pd.DataFrame:
    features = add_money_flow_features(stock_daily)
    latest = (
        features.sort_values(["ticker", "date"])
        .groupby("ticker", as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )
    return latest
