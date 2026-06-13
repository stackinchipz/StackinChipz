"""Chaikin Power Gauge (public approximation).

The Chaikin Power Gauge rates a stock across four buckets and rolls them into a
Bullish / Neutral / Bearish verdict. The original engine only had the
*Technicals* bucket (CMF money flow + trend + RS). This adds the missing three
using the data we now pull, producing a fuller gauge:

    Financials  -> Uniform ROA, ROIIC, debt (from capital-efficiency layer)
    Earnings    -> revenue growth, margin trend, incremental margin
    Technicals  -> money-flow + trend + relative-strength scores (existing)
    Experts     -> options-flow conviction (ask-side / repeat flow / catalyst)
                   as a public stand-in for analyst/insider activity

This is a logic-pattern approximation, not Chaikin Analytics' proprietary model.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG


def _band(value, lo, hi, points):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    return float(np.clip((float(value) - lo) / (hi - lo + 1e-9), 0.0, 1.0) * points)


def financials_bucket(row: pd.Series, config: ScannerConfig) -> float:
    coc = config.cost_of_capital
    s = 0.0
    s += _band(row.get("uniform_roa"), coc, 0.30, 45.0)
    s += _band(row.get("roiic"), coc, coc + 0.25, 40.0)
    s += _band(row.get("uniform_roa_trend"), -0.02, 0.06, 15.0)
    return float(np.clip(s, 0, 100))


def earnings_bucket(row: pd.Series) -> float:
    s = 0.0
    s += _band(row.get("revenue_cagr"), 0.0, 0.30, 40.0)
    s += _band(row.get("op_margin_trend"), -0.02, 0.04, 30.0)
    s += _band(row.get("incr_op_margin"), 0.0, 0.35, 30.0)
    return float(np.clip(s, 0, 100))


def technicals_bucket(row: pd.Series) -> float:
    # Reuse the existing 0-100 component scores.
    mf = float(row.get("money_flow_score", 50.0) or 50.0)
    trend = float(row.get("trend_score", 50.0) or 50.0)
    rs = float(row.get("rs_score", 50.0) or 50.0)
    return float(np.clip(0.45 * mf + 0.35 * trend + 0.20 * rs, 0, 100))


def experts_bucket(row: pd.Series) -> float:
    # Options-flow conviction as a public proxy for "expert activity".
    ask = float(row.get("ask_side_ratio", 0.5) or 0.5)
    repeat = float(row.get("repeat_flow_score", 0.5) or 0.5)
    catalyst = float(row.get("catalyst_score", 50.0) or 50.0)
    catalyst = catalyst / 100.0 if catalyst > 1 else catalyst
    s = ask * 45.0 + repeat * 30.0 + catalyst * 25.0
    return float(np.clip(s, 0, 100))


def power_gauge_score(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> float:
    w = config.power_gauge_weights
    score = (
        financials_bucket(row, config) * w["financials"]
        + earnings_bucket(row) * w["earnings"]
        + technicals_bucket(row) * w["technicals"]
        + experts_bucket(row) * w["experts"]
    )
    return round(float(np.clip(score, 0, 100)), 2)


def power_gauge_rating(score: float) -> str:
    if pd.isna(score):
        return "Neutral"
    if score >= 65:
        return "Bullish"
    if score >= 55:
        return "Bullish (Mod)"
    if score <= 35:
        return "Bearish"
    if score <= 45:
        return "Bearish (Mod)"
    return "Neutral"


def add_power_gauge(df: pd.DataFrame, config: ScannerConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    out = df.copy()
    out["pg_financials"] = out.apply(lambda r: financials_bucket(r, config), axis=1)
    out["pg_earnings"] = out.apply(earnings_bucket, axis=1)
    out["pg_technicals"] = out.apply(technicals_bucket, axis=1)
    out["pg_experts"] = out.apply(experts_bucket, axis=1)
    out["power_gauge_score"] = out.apply(lambda r: power_gauge_score(r, config), axis=1)
    out["power_gauge_rating"] = out["power_gauge_score"].apply(power_gauge_rating)
    return out
