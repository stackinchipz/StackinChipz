"""Tests for point-in-time fundamentals and the IV-history store."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.config import DEFAULT_CONFIG
from signalos.data_sources.fundamentals import make_demo_fundamentals, as_of
from signalos.features.capital_efficiency import compute_capital_efficiency
from signalos.data_sources.iv_store import (
    atm_iv_snapshot, append_iv_snapshot, load_iv_history,
)
from signalos.features.iv_regime import compute_iv_regime


# --- Point-in-time fundamentals ---
def test_as_of_excludes_future_filings():
    f = make_demo_fundamentals()
    assert "filing_date" in f.columns
    latest_fy = int(f["fiscal_year"].max())
    # Cut off before the latest FY's 10-K would have been filed.
    cut = f[f["fiscal_year"] == latest_fy]["filing_date"].iloc[0]
    cut = pd.to_datetime(cut) - pd.Timedelta(days=1)
    filtered = as_of(f, cut)
    assert filtered["fiscal_year"].max() < latest_fy


def test_compute_capital_efficiency_respects_asof():
    f = make_demo_fundamentals()
    full = compute_capital_efficiency(f, DEFAULT_CONFIG)
    early = compute_capital_efficiency(f, DEFAULT_CONFIG, asof_date="2000-01-01")
    assert not full.empty
    assert early.empty          # nothing filed by 2000


def test_as_of_keeps_unknown_filing_dates():
    f = make_demo_fundamentals().copy()
    f["filing_date"] = np.nan
    assert len(as_of(f, "2020-01-01")) == len(f)   # NaT kept (conservative)


# --- IV-history store ---
def _chain(iv_by_ticker):
    rows = []
    for t, iv in iv_by_ticker.items():
        rows += [
            {"ticker": t, "type": "call", "strike": 100, "delta": 0.5, "mid": 5,
             "implied_volatility": iv, "days_to_expiration": 30, "date": "2025-01-10"},
            {"ticker": t, "type": "put", "strike": 100, "delta": -0.5, "mid": 5,
             "implied_volatility": iv, "days_to_expiration": 30, "date": "2025-01-10"},
        ]
    return pd.DataFrame(rows)


def test_atm_iv_snapshot_extracts_per_ticker():
    snap = atm_iv_snapshot(_chain({"AAA": 0.4, "BBB": 0.6}))
    assert set(snap["ticker"]) == {"AAA", "BBB"}
    assert "atm_iv" in snap.columns


def test_store_append_dedup_and_load(tmp_path):
    store = tmp_path / "iv_history.csv"
    for i, iv in enumerate([0.30, 0.35, 0.40, 0.55]):
        c = _chain({"AAA": iv})
        c["date"] = f"2025-01-{10+i:02d}"
        append_iv_snapshot(c, store, snapshot_date=f"2025-01-{10+i:02d}")
    # Re-append same date -> dedup, not duplicate.
    append_iv_snapshot(_chain({"AAA": 0.55}), store, snapshot_date="2025-01-13")
    hist = load_iv_history(store)
    assert len(hist[hist["ticker"] == "AAA"]) == 4


def test_true_iv_rank_uses_history(tmp_path):
    store = tmp_path / "iv_history.csv"
    # Build 30 days of low IV history for AAA, then a high current reading.
    for d in range(30):
        c = _chain({"AAA": 0.25})
        append_iv_snapshot(c, store, snapshot_date=f"2025-02-{d+1:02d}")
    hist = load_iv_history(store)
    current = _chain({"AAA": 0.60})   # well above the trailing distribution
    ivr = compute_iv_regime(current, iv_history=hist, config=DEFAULT_CONFIG)
    assert ivr.iloc[0]["iv_rank"] >= 90    # true rank: today far above its own year
