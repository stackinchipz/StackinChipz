import numpy as np
import pandas as pd
from signalos.config import ScannerConfig, DEFAULT_CONFIG


def option_spread_pct(row: pd.Series) -> float:
    bid = float(row.get("bid", 0) or 0)
    ask = float(row.get("ask", 0) or 0)
    mid = float(row.get("mid", 0) or 0)
    if mid <= 0:
        mid = (bid + ask) / 2 if (bid + ask) > 0 else np.nan
    if pd.isna(mid) or mid <= 0:
        return 1.0
    return max(0.0, (ask - bid) / mid)


def score_option_liquidity(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> float:
    score = 100.0
    spread_pct = option_spread_pct(row)
    oi = float(row.get("open_interest", 0) or 0)
    volume = float(row.get("volume", 0) or 0)
    premium = float(row.get("premium_traded", 0) or 0)

    if spread_pct > config.max_option_spread_pct:
        score -= 45
    elif spread_pct > config.preferred_max_option_spread_pct:
        score -= 20

    if oi < config.min_open_interest:
        score -= 20

    if volume < config.min_option_volume:
        score -= 20

    if premium < config.min_premium_traded:
        score -= 15

    return max(0.0, min(100.0, score))
