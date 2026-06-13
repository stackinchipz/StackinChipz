import numpy as np
import pandas as pd


def add_option_features(option_chain: pd.DataFrame) -> pd.DataFrame:
    df = option_chain.copy()

    for col in ["bid", "ask", "mid", "last", "volume", "open_interest", "avg_contract_volume_20d"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "mid" not in df.columns or (df["mid"] <= 0).all():
        df["mid"] = (df["bid"] + df["ask"]) / 2

    df["premium_traded"] = df["volume"] * df["mid"] * 100
    df["volume_to_oi"] = df["volume"] / df["open_interest"].replace(0, np.nan)
    df["volume_to_oi"] = df["volume_to_oi"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["volume_vs_avg"] = df["volume"] / df["avg_contract_volume_20d"].replace(0, np.nan)
    df["volume_vs_avg"] = df["volume_vs_avg"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["contract_volume_z"] = 0.0
    for ticker, g_idx in df.groupby("ticker").groups.items():
        idx = list(g_idx)
        vols = df.loc[idx, "volume"].astype(float)
        mu = vols.mean()
        sigma = vols.std(ddof=0)
        if sigma == 0 or pd.isna(sigma):
            z = pd.Series(0.0, index=idx)
        else:
            z = (vols - mu) / sigma
        df.loc[idx, "contract_volume_z"] = z.clip(lower=0)

    df["premium_percentile"] = (
        df.groupby("ticker")["premium_traded"]
        .rank(pct=True)
        .fillna(0)
    )

    for col in ["ask_side_ratio", "repeat_flow_score", "catalyst_score"]:
        if col not in df.columns:
            df[col] = 0.5

    return df


def score_uoa(row: pd.Series) -> float:
    score = 0.0
    score += min(float(row.get("contract_volume_z", 0)) * 8.0, 25.0)
    score += min(float(row.get("premium_percentile", 0)) * 25.0, 25.0)
    score += min(float(row.get("volume_to_oi", 0)) * 8.0, 20.0)
    score += min(float(row.get("ask_side_ratio", 0.5)) * 15.0, 15.0)
    score += min(float(row.get("repeat_flow_score", 0.5)) * 10.0, 10.0)

    delta = abs(float(row.get("delta", 0.0) or 0.0))
    dte = float(row.get("days_to_expiration", 0.0) or 0.0)
    if 0.25 <= delta <= 0.70:
        score += 2.5
    if 14 <= dte <= 120:
        score += 2.5

    return max(0.0, min(100.0, score))


def infer_bias(row: pd.Series) -> str:
    option_type = str(row.get("type", "")).lower()
    ask_side = float(row.get("ask_side_ratio", 0.5))
    if option_type == "call" and ask_side >= 0.55:
        return "Bullish"
    if option_type == "put" and ask_side >= 0.55:
        return "Bearish"
    return "Unclear"


def select_top_contracts(option_chain: pd.DataFrame, max_per_ticker: int = 3) -> pd.DataFrame:
    features = add_option_features(option_chain)
    features["uoa_score"] = features.apply(score_uoa, axis=1)
    features["bias"] = features.apply(infer_bias, axis=1)
    features = features[features["bias"] != "Unclear"].copy()
    features = features.sort_values(["ticker", "bias", "uoa_score", "premium_traded"], ascending=[True, True, False, False])
    top = (
        features.groupby(["ticker", "bias"], as_index=False)
        .head(max_per_ticker)
        .reset_index(drop=True)
    )
    return top
