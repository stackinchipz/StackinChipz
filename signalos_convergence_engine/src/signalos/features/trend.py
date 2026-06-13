import numpy as np
import pandas as pd


def score_trend(row: pd.Series) -> float:
    score = 50.0
    close = row.get("close", np.nan)
    sma_20 = row.get("sma_20", np.nan)
    sma_50 = row.get("sma_50", np.nan)
    return_20d = row.get("return_20d", 0)
    volume_ratio = row.get("volume_ratio_20d", 1)

    if pd.notna(close) and pd.notna(sma_20) and close > sma_20:
        score += 15
    if pd.notna(sma_20) and pd.notna(sma_50) and sma_20 > sma_50:
        score += 15
    if return_20d > 0.05:
        score += 10
    if volume_ratio > 1.2 and return_20d > 0:
        score += 10

    return max(0.0, min(100.0, score))


def score_relative_strength(row: pd.Series) -> float:
    rs = float(row.get("rs_rank", 50.0))
    return max(0.0, min(100.0, rs))
