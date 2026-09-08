"""Score expert/sentiment inputs into the engine's 0-100 convention.

Produces per-ticker:
    revision_score  - estimate-revision momentum (one of the most robust public factors)
    insider_score   - net insider buying
    squeeze_score   - short-interest fuel (short_interest_pct + days_to_cover)

These feed the Chaikin Power Gauge "Experts" bucket and the SQUEEZE options
screen. Designed to be additive: when absent, the Power Gauge falls back to the
options-flow-only experts value, so existing behavior is unchanged.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _band(value, lo, hi, points=100.0):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return np.nan
    return float(np.clip((float(value) - lo) / (hi - lo + 1e-9), 0.0, 1.0) * points)


def revision_score(net: float) -> float:
    # -10% net revisions -> 0, +40% -> 100; 0 maps to ~20.
    return _band(net, -0.10, 0.40)


def insider_score(ratio: float) -> float:
    # ratio in [-1, 1]; 0 -> 50 (neutral), +1 -> 100, -1 -> 0.
    if ratio is None or pd.isna(ratio):
        return np.nan
    return float(np.clip(50.0 + 50.0 * float(ratio), 0.0, 100.0))


def squeeze_score(short_interest_pct: float, days_to_cover: float) -> float:
    si = _band(short_interest_pct, 0.05, 0.30, 100.0)
    dtc = _band(days_to_cover, 1.0, 10.0, 100.0)
    if pd.isna(si) and pd.isna(dtc):
        return np.nan
    si = 0.0 if pd.isna(si) else si
    dtc = 0.0 if pd.isna(dtc) else dtc
    return float(np.clip(0.6 * si + 0.4 * dtc, 0.0, 100.0))


def compute_expert_signals(expert_inputs: pd.DataFrame) -> pd.DataFrame:
    if expert_inputs is None or expert_inputs.empty:
        return pd.DataFrame(columns=["ticker", "revision_score", "insider_score", "squeeze_score"])
    df = expert_inputs.copy()
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df["revision_score"] = df["estimate_revision_net"].apply(revision_score)
    df["insider_score"] = df["insider_net_ratio"].apply(insider_score)
    df["squeeze_score"] = df.apply(
        lambda r: squeeze_score(r.get("short_interest_pct"), r.get("days_to_cover")), axis=1)
    return df[["ticker", "revision_score", "insider_score", "squeeze_score"]]
