import pandas as pd
from signalos.config import ScannerConfig, DEFAULT_CONFIG


def compute_convergence_score(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> float:
    weights = config.convergence_weights
    score = 0.0
    for col, weight in weights.items():
        score += float(row.get(col, 0.0) or 0.0) * weight
    return round(max(0.0, min(100.0, score)), 2)


def classify_signal(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> str:
    uoa = float(row.get("uoa_score", 0.0) or 0.0)
    mf = float(row.get("money_flow_score", 0.0) or 0.0)
    liq = float(row.get("liquidity_score", 0.0) or 0.0)

    if uoa >= config.strong_uoa_score and mf >= config.strong_money_flow_score and liq >= config.min_liquidity_score:
        return "A+ setup"

    if uoa >= config.min_uoa_score and mf >= config.min_money_flow_score and liq >= config.min_liquidity_score:
        return "Tradable"

    if uoa >= config.min_uoa_score and mf < 50:
        return "Reject"

    if liq < config.min_liquidity_score:
        return "Reject"

    return "Watchlist"


def reject_reason(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> str:
    reasons = []

    if float(row.get("uoa_score", 0) or 0) < config.min_uoa_score:
        reasons.append("UOA below threshold")

    if float(row.get("money_flow_score", 0) or 0) < config.min_money_flow_score:
        reasons.append("Money flow does not confirm direction")

    if float(row.get("liquidity_score", 0) or 0) < config.min_liquidity_score:
        reasons.append("Option liquidity/spread quality too weak")

    if row.get("bias", "") == "Unclear":
        reasons.append("Directional inference unclear")

    return "; ".join(reasons) if reasons else "None"
