import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG
from signalos.features.money_flow import latest_money_flow_snapshot
from signalos.features.unusual_options import select_top_contracts
from signalos.features.trend import score_trend, score_relative_strength
from signalos.features.liquidity import score_option_liquidity, option_spread_pct
from signalos.scoring.money_flow_score import score_money_flow
from signalos.scoring.convergence import compute_convergence_score, classify_signal, reject_reason
from signalos.trade_construction.structures import suggest_structure, suggested_risk_rules


def run_daily_scan(
    stock_daily: pd.DataFrame,
    option_chain_latest: pd.DataFrame,
    config: ScannerConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """
    Core scanner.

    Important: the stock feature set is clipped to the option-chain signal date
    to avoid look-ahead leakage in demos/backtests.
    """
    options = option_chain_latest.copy()
    options["date"] = pd.to_datetime(options["date"])
    signal_date = options["date"].max()

    stocks = stock_daily.copy()
    stocks["date"] = pd.to_datetime(stocks["date"])
    stocks = stocks[stocks["date"] <= signal_date].copy()

    mf = latest_money_flow_snapshot(stocks)
    top_options = select_top_contracts(options, max_per_ticker=3)
    merged = top_options.merge(mf, on="ticker", how="left", suffixes=("", "_stock"))

    merged["date"] = signal_date.date().isoformat()

    merged["money_flow_score"] = merged.apply(lambda r: score_money_flow(r, r["bias"], config), axis=1)
    merged["trend_score"] = merged.apply(score_trend, axis=1)
    merged["rs_score"] = merged.apply(score_relative_strength, axis=1)
    merged["spread_pct"] = merged.apply(option_spread_pct, axis=1)
    merged["liquidity_score"] = merged.apply(lambda r: score_option_liquidity(r, config), axis=1)

    if "catalyst_score" not in merged.columns:
        merged["catalyst_score"] = 50.0
    else:
        merged["catalyst_score"] = pd.to_numeric(merged["catalyst_score"], errors="coerce").fillna(0.5)
        if merged["catalyst_score"].max() <= 1.0:
            merged["catalyst_score"] = merged["catalyst_score"] * 100

    merged["convergence_score"] = merged.apply(lambda r: compute_convergence_score(r, config), axis=1)
    merged["decision"] = merged.apply(lambda r: classify_signal(r, config), axis=1)
    merged["reject_reason"] = merged.apply(lambda r: reject_reason(r, config), axis=1)
    merged["suggested_structure"] = merged.apply(suggest_structure, axis=1)
    merged["risk_rules"] = merged.apply(suggested_risk_rules, axis=1)

    preferred_cols = [
        "date", "ticker", "bias", "decision", "convergence_score",
        "uoa_score", "money_flow_score", "trend_score", "rs_score",
        "liquidity_score", "catalyst_score", "spread_pct", "reject_reason",
        "suggested_structure", "risk_rules",
        "option_symbol", "expiration", "strike", "type", "bid", "ask", "mid",
        "volume", "open_interest", "avg_contract_volume_20d",
        "premium_traded", "volume_to_oi", "ask_side_ratio", "repeat_flow_score",
        "delta", "gamma", "theta", "vega", "implied_volatility", "days_to_expiration",
        "cmf_5", "cmf_21", "cmf_63", "close", "sma_20", "sma_50", "rs_rank"
    ]

    cols = [c for c in preferred_cols if c in merged.columns]
    out = merged[cols].copy()

    priority = {"A+ setup": 0, "Tradable": 1, "Watchlist": 2, "Reject": 3}
    out["_priority"] = out["decision"].map(priority).fillna(9)
    out = out.sort_values(["_priority", "convergence_score"], ascending=[True, False]).drop(columns="_priority")
    return out.reset_index(drop=True)
