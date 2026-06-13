"""Score the capital-efficiency metrics into a 0-100 score + a verdict.

Verdict taxonomy:
    Compounder        - high & rising Uniform ROA, ROIIC > cost of capital,
                        growth capex (capex/dep > 1), expanding margins.
    Quality           - solid returns, less aggressive reinvestment.
    Neutral           - mixed signals.
    Capital Destroyer - heavy capex that ISN'T translating into returns
                        (low/negative ROIIC, compressing margins). Short candidate.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG


def _band(value: float, lo: float, hi: float, points: float) -> float:
    """Linear 0..points as value moves lo->hi (clamped)."""
    if pd.isna(value):
        return 0.0
    return float(np.clip((value - lo) / (hi - lo + 1e-9), 0.0, 1.0) * points)


def score_capital_efficiency(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> float:
    coc = config.cost_of_capital
    score = 0.0
    # Uniform ROA level (0-25): coc -> 30%.
    score += _band(row.get("uniform_roa"), coc, 0.30, 25.0)
    # ROIIC vs cost of capital (0-30): the heart of "is new capital earning?".
    score += _band(row.get("roiic"), coc, coc + 0.25, 30.0)
    # Capex productivity (0-20): revenue created per $ capex.
    score += _band(row.get("incr_rev_per_capex"), 0.5, 3.0, 12.0)
    score += _band(row.get("capex_to_depreciation"), 1.0, 2.0, 8.0)
    # Profitable growth (0-15): incremental margin + uniform ROA trend.
    score += _band(row.get("incr_op_margin"), 0.0, 0.35, 8.0)
    score += _band(row.get("uniform_roa_trend"), 0.0, 0.06, 7.0)
    # Top-line momentum (0-10).
    score += _band(row.get("revenue_cagr"), 0.05, 0.30, 10.0)
    return round(float(np.clip(score, 0.0, 100.0)), 2)


def capital_efficiency_verdict(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> str:
    uroa = row.get("uniform_roa")
    roiic = row.get("roiic")
    capex_dep = row.get("capex_to_depreciation")
    margin_trend = row.get("op_margin_trend")

    # Heavy reinvestment (capex > depreciation) earning sub-cost-of-capital
    # returns while profitability deteriorates = capital destruction.
    # Use margin TREND, not incremental margin: Δincome/Δrevenue flips positive
    # and misleads when revenue is flat/declining.
    is_destroyer = (
        pd.notna(roiic) and roiic < config.destroyer_max_roiic and
        pd.notna(capex_dep) and capex_dep > config.compounder_min_capex_to_depreciation and
        (pd.isna(margin_trend) or margin_trend < 0)
    )
    if is_destroyer:
        return "Capital Destroyer"

    is_compounder = (
        pd.notna(uroa) and uroa >= config.compounder_min_uniform_roa and
        pd.notna(roiic) and roiic >= config.compounder_min_roiic and
        pd.notna(capex_dep) and capex_dep >= config.compounder_min_capex_to_depreciation
    )
    if is_compounder:
        return "Compounder"

    if pd.notna(uroa) and uroa >= config.compounder_min_uniform_roa:
        return "Quality"

    return "Neutral"


def add_capital_efficiency_scores(metrics: pd.DataFrame,
                                  config: ScannerConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    if metrics is None or metrics.empty:
        return metrics
    out = metrics.copy()
    out["capital_efficiency_score"] = out.apply(lambda r: score_capital_efficiency(r, config), axis=1)
    out["capital_verdict"] = out.apply(lambda r: capital_efficiency_verdict(r, config), axis=1)
    return out
