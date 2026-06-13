import pandas as pd
from signalos.config import ScannerConfig, DEFAULT_CONFIG


def score_money_flow(row: pd.Series, bias: str, config: ScannerConfig = DEFAULT_CONFIG) -> float:
    score = 50.0
    cmf_5 = float(row.get("cmf_5", 0.0) or 0.0)
    cmf_21 = float(row.get("cmf_21", 0.0) or 0.0)
    close = float(row.get("close", 0.0) or 0.0)
    sma_20 = row.get("sma_20")
    sma_50 = row.get("sma_50")
    rs_rank = float(row.get("rs_rank", 50.0) or 50.0)

    if bias == "Bullish":
        if cmf_21 > config.bullish_cmf_confirm:
            score += 15
        if cmf_21 > config.bullish_cmf_strong:
            score += 15
        if cmf_5 > cmf_21:
            score += 10
        if pd.notna(sma_20) and close > float(sma_20):
            score += 5
        if pd.notna(sma_20) and pd.notna(sma_50) and float(sma_20) > float(sma_50):
            score += 5
        if rs_rank > 70:
            score += 10

    elif bias == "Bearish":
        if cmf_21 < config.bearish_cmf_confirm:
            score += 15
        if cmf_21 < config.bearish_cmf_strong:
            score += 15
        if cmf_5 < cmf_21:
            score += 10
        if pd.notna(sma_20) and close < float(sma_20):
            score += 5
        if pd.notna(sma_20) and pd.notna(sma_50) and float(sma_20) < float(sma_50):
            score += 5
        if rs_rank < 30:
            score += 10

    return max(0.0, min(100.0, score))
