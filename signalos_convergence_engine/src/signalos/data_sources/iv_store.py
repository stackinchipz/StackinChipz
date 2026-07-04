"""IV-history store — persist daily ATM IV per ticker for a true 52-week IV rank.

A single option-chain snapshot has no history, so `iv_regime` falls back to a
cross-sectional IV rank. Appending each day's ATM IV to a CSV store lets
`compute_iv_regime(chain, iv_history=...)` compute a real per-name 52-week rank
(the percentile of today's ATM IV within that name's own trailing year).

Store schema: ticker, date, atm_iv  (one row per ticker per day).
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from signalos.features.iv_regime import _atm_row


def atm_iv_snapshot(option_chain: pd.DataFrame, snapshot_date: str | None = None) -> pd.DataFrame:
    """One (ticker, date, atm_iv) row per ticker from a chain snapshot."""
    if option_chain is None or option_chain.empty:
        return pd.DataFrame(columns=["ticker", "date", "atm_iv"])
    df = option_chain.copy()
    for c in ["implied_volatility", "delta", "days_to_expiration"]:
        df[c] = pd.to_numeric(df.get(c), errors="coerce")
    if snapshot_date is None:
        snapshot_date = str(pd.to_datetime(df["date"]).max().date()) if "date" in df.columns else ""
    rows = []
    for ticker, g in df.groupby("ticker", sort=False):
        atm = _atm_row(g)
        iv = float(atm.get("implied_volatility") or np.nan)
        if pd.notna(iv):
            rows.append({"ticker": str(ticker).upper(), "date": snapshot_date, "atm_iv": iv})
    return pd.DataFrame(rows)


def append_iv_snapshot(option_chain: pd.DataFrame, store_path: str | Path,
                       snapshot_date: str | None = None) -> Path:
    """Append today's ATM IV snapshot to the store (dedup on ticker+date)."""
    store_path = Path(store_path)
    snap = atm_iv_snapshot(option_chain, snapshot_date)
    if store_path.exists():
        existing = pd.read_csv(store_path)
        combined = pd.concat([existing, snap], ignore_index=True)
    else:
        store_path.parent.mkdir(parents=True, exist_ok=True)
        combined = snap
    combined = (combined.drop_duplicates(subset=["ticker", "date"], keep="last")
                .sort_values(["ticker", "date"]).reset_index(drop=True))
    combined.to_csv(store_path, index=False)
    return store_path


def load_iv_history(store_path: str | Path, lookback_days: int = 365,
                    asof_date: str | None = None) -> pd.DataFrame:
    """Load the store as an iv_history frame (ticker, date, atm_iv).

    Trimmed to the trailing `lookback_days`, and to on/before `asof_date` if given
    (point-in-time for backtests).
    """
    store_path = Path(store_path)
    if not store_path.exists():
        return pd.DataFrame(columns=["ticker", "date", "atm_iv"])
    df = pd.read_csv(store_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if asof_date is not None:
        df = df[df["date"] <= pd.to_datetime(asof_date)]
    if not df.empty:
        cutoff = df["date"].max() - pd.Timedelta(days=lookback_days)
        df = df[df["date"] >= cutoff]
    return df.reset_index(drop=True)
