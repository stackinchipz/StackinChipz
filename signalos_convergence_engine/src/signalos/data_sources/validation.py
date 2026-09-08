from __future__ import annotations

import pandas as pd


REQUIRED_STOCK_COLUMNS = {
    "date", "ticker", "open", "high", "low", "close", "volume"
}

REQUIRED_OPTION_COLUMNS = {
    "date", "ticker", "option_symbol", "expiration", "strike", "type",
    "bid", "ask", "mid", "last", "volume", "open_interest",
    "avg_contract_volume_20d", "implied_volatility", "delta", "gamma",
    "theta", "vega", "days_to_expiration", "ask_side_ratio",
    "repeat_flow_score", "catalyst_score"
}


def validate_stock_daily(df: pd.DataFrame) -> None:
    missing = REQUIRED_STOCK_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"stock_daily missing required columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("stock_daily is empty")

    if (pd.to_numeric(df["volume"], errors="coerce").fillna(-1) < 0).any():
        raise ValueError("stock_daily contains negative volume")

    for col in ["open", "high", "low", "close"]:
        if (pd.to_numeric(df[col], errors="coerce").fillna(-1) <= 0).any():
            raise ValueError(f"stock_daily contains invalid {col} values")


def validate_option_chain(df: pd.DataFrame) -> None:
    missing = REQUIRED_OPTION_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"option_chain missing required columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("option_chain is empty")

    option_types = set(df["type"].astype(str).str.lower().unique())
    if not option_types.issubset({"call", "put"}):
        raise ValueError(f"option_chain type must be call/put. Found: {sorted(option_types)}")

    bid = pd.to_numeric(df["bid"], errors="coerce")
    ask = pd.to_numeric(df["ask"], errors="coerce")
    if (ask < bid).any():
        raise ValueError("option_chain contains ask < bid")

    if (pd.to_numeric(df["mid"], errors="coerce").fillna(-1) <= 0).any():
        raise ValueError("option_chain contains invalid mid values")
