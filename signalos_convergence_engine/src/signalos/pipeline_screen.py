"""Full Capital-Compounder screen: fuses options flow + fundamentals + IV regime.

This is the merged engine the new modules feed into. Pipeline:

    1. run_daily_scan        -> options-flow convergence base (UOA + money flow)
    2. capital efficiency    -> Uniform-ROA-lite, ROIIC, capex productivity, verdict
    3. IV regime             -> iv_rank, expected move, skew, regime
    4. Chaikin Power Gauge   -> 4-bucket Bullish/Neutral/Bearish rating
    5. re-score convergence  -> now includes the fundamental conviction layer
    6. options screens       -> named patterns + regime-aware trade suggestions
    7. risk engine           -> position sizing + portfolio heat + book Greeks

Everything is broker-agnostic: the output is a ranked candidate table an analyst
(or, later, a guarded agent) consumes.
"""
from __future__ import annotations

import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG
from signalos.pipeline import run_daily_scan
from signalos.features.capital_efficiency import compute_capital_efficiency
from signalos.features.iv_regime import compute_iv_regime
from signalos.scoring.capital_efficiency_score import add_capital_efficiency_scores
from signalos.scoring.chaikin_power_gauge import add_power_gauge
from signalos.scoring.convergence import compute_convergence_score
from signalos.trade_construction.options_screens import add_options_screens
from signalos.risk import apply_risk_engine, RiskState


def run_full_screen(
    stock_daily: pd.DataFrame,
    option_chain_latest: pd.DataFrame,
    fundamentals: pd.DataFrame | None = None,
    iv_history: pd.DataFrame | None = None,
    sector_map: pd.DataFrame | None = None,
    earnings: pd.DataFrame | None = None,
    config: ScannerConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    # 1. Options-flow convergence base.
    base = run_daily_scan(stock_daily, option_chain_latest, config)

    # 2. Capital efficiency (Uniform-ROA-lite + ROIIC + capex productivity).
    if fundamentals is not None and not fundamentals.empty:
        cap = add_capital_efficiency_scores(
            compute_capital_efficiency(fundamentals, config), config)
        base = base.merge(cap, on="ticker", how="left", suffixes=("", "_cap"))
    else:
        base["capital_efficiency_score"] = 50.0
        base["capital_verdict"] = "Unknown"

    # 3. IV regime.
    ivr = compute_iv_regime(option_chain_latest, iv_history, config)
    if not ivr.empty:
        base = base.merge(ivr, on="ticker", how="left")

    # 4. Earnings calendar -> days-to-earnings (IV-crush guard input).
    if earnings is not None and not earnings.empty and "next_earnings" in earnings.columns:
        e = earnings.copy()
        e["next_earnings"] = pd.to_datetime(e["next_earnings"], errors="coerce")
        today = pd.Timestamp.today().normalize()
        e["earnings_dte"] = (e["next_earnings"] - today).dt.days
        base = base.merge(e[["ticker", "earnings_dte"]], on="ticker", how="left")
    else:
        base["earnings_dte"] = float("nan")

    # 5. Chaikin Power Gauge (needs technical + fundamental columns now present).
    base["capital_efficiency_score"] = base["capital_efficiency_score"].fillna(50.0)
    base = add_power_gauge(base, config)

    # 6. Re-score convergence so the fundamental layer is included, then re-rank.
    base["convergence_score"] = base.apply(lambda r: compute_convergence_score(r, config), axis=1)

    # 7. Sector map (for sector-heat caps in the risk engine).
    if sector_map is not None and not sector_map.empty:
        base = base.merge(sector_map, on="ticker", how="left")
    if "sector" not in base.columns:
        base["sector"] = "Unknown"
    base["sector"] = base["sector"].fillna("Unknown")

    # 8. Named options screens + regime-aware trade suggestions.
    base = add_options_screens(base, config)

    priority = {"A+ setup": 0, "Tradable": 1, "Watchlist": 2, "Reject": 3}
    base["_p"] = base["decision"].map(priority).fillna(9)
    base = base.sort_values(["_p", "convergence_score"], ascending=[True, False]).drop(columns="_p")
    return base.reset_index(drop=True)


def size_screen(signals: pd.DataFrame, config: ScannerConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    """Apply the risk engine to a screened table; returns sized tradable rows.

    Book-level summary (heat, net Greeks) is attached on `.attrs['book']`.
    """
    state = RiskState(account_size=config.account_size)
    return apply_risk_engine(signals, config, state)
