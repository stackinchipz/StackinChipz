"""Implied-volatility regime feature (drives options structure selection).

For a premium-buying book this is both an alpha and a risk gate: don't pay up
for options when IV is rich. From an option-chain snapshot per ticker we derive:

- atm_iv          : ATM implied vol (nearest-the-money contract)
- iv_rank         : 0-100 rank of atm_iv vs the cross-sectional / historical band
- expected_move   : 1-expiration expected move (ATM straddle / spot), as a %
- skew            : put_iv - call_iv at ~25-delta wings (positioning tell)
- regime          : Low / Normal / High / Extreme

iv_rank ideally uses each name's own 1y IV history. A chain snapshot has no
history, so when none is supplied we approximate rank from the per-name IV
term/strike distribution and a cross-sectional fallback. Pass `iv_history`
(columns: ticker, date, atm_iv) to compute a true 52-week IV rank.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG


def _atm_row(g: pd.DataFrame) -> pd.Series:
    """Nearest-to-the-money contract by |delta - 0.5|, nearest expiration."""
    gg = g.copy()
    gg["abs_delta"] = gg["delta"].abs()
    gg["atm_dist"] = (gg["abs_delta"] - 0.5).abs()
    nearest_dte = gg["days_to_expiration"].min()
    front = gg[gg["days_to_expiration"] <= nearest_dte + 20]
    if front.empty:
        front = gg
    return front.sort_values("atm_dist").iloc[0]


def _regime(iv_rank: float, config: ScannerConfig) -> str:
    if pd.isna(iv_rank):
        return "Unknown"
    if iv_rank >= config.iv_rank_extreme:
        return "Extreme"
    if iv_rank >= config.iv_rank_high:
        return "High"
    if iv_rank <= config.iv_rank_low:
        return "Low"
    return "Normal"


def compute_iv_regime(
    option_chain: pd.DataFrame,
    iv_history: pd.DataFrame | None = None,
    config: ScannerConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """One IV-regime row per ticker."""
    if option_chain is None or option_chain.empty:
        return pd.DataFrame()

    df = option_chain.copy()
    for c in ["implied_volatility", "delta", "strike", "mid", "days_to_expiration"]:
        df[c] = pd.to_numeric(df.get(c), errors="coerce")

    rows = []
    # Cross-sectional band for the fallback rank.
    xs_atm = []
    per_ticker_atm = {}
    for ticker, g in df.groupby("ticker", sort=False):
        atm = _atm_row(g)
        atm_iv = float(atm.get("implied_volatility") or np.nan)
        per_ticker_atm[ticker] = atm_iv
        if pd.notna(atm_iv):
            xs_atm.append(atm_iv)
    xs_lo, xs_hi = (np.percentile(xs_atm, 5), np.percentile(xs_atm, 95)) if xs_atm else (0.2, 0.9)

    hist_grp = None
    if iv_history is not None and not iv_history.empty:
        h = iv_history.copy()
        h["atm_iv"] = pd.to_numeric(h["atm_iv"], errors="coerce")
        hist_grp = {t: g["atm_iv"].dropna() for t, g in h.groupby("ticker")}

    for ticker, g in df.groupby("ticker", sort=False):
        atm = _atm_row(g)
        spot_proxy = float(atm.get("strike") or np.nan)
        atm_iv = per_ticker_atm.get(ticker, np.nan)
        dte = float(atm.get("days_to_expiration") or np.nan)

        # True 52w IV rank if history available; else cross-sectional fallback.
        if hist_grp and ticker in hist_grp and len(hist_grp[ticker]) >= 20 and pd.notna(atm_iv):
            series = hist_grp[ticker]
            iv_rank = float((series < atm_iv).mean() * 100.0)
        elif pd.notna(atm_iv):
            iv_rank = float(np.clip((atm_iv - xs_lo) / (xs_hi - xs_lo + 1e-9) * 100.0, 0, 100))
        else:
            iv_rank = np.nan

        # Expected move from the ATM straddle (call mid + put mid at ATM strike).
        atm_strike = atm.get("strike")
        near = g[(g["days_to_expiration"] <= g["days_to_expiration"].min() + 20)]
        straddle = near[np.isclose(near["strike"], atm_strike)]
        call_mid = straddle[straddle["type"].str.lower() == "call"]["mid"].max()
        put_mid = straddle[straddle["type"].str.lower() == "put"]["mid"].max()
        if pd.notna(call_mid) and pd.notna(put_mid) and spot_proxy and spot_proxy > 0:
            expected_move = (call_mid + put_mid) / spot_proxy
        elif pd.notna(atm_iv) and pd.notna(dte):
            expected_move = atm_iv * np.sqrt(max(dte, 1) / 365.0)
        else:
            expected_move = np.nan

        # Wing skew: ~25-delta put IV minus ~25-delta call IV.
        calls = g[g["type"].str.lower() == "call"]
        puts = g[g["type"].str.lower() == "put"]
        c_iv = _delta_iv(calls, 0.25)
        p_iv = _delta_iv(puts, -0.25)
        skew = (p_iv - c_iv) if pd.notna(c_iv) and pd.notna(p_iv) else np.nan

        rows.append({
            "ticker": ticker,
            "atm_iv": atm_iv,
            "iv_rank": iv_rank,
            "expected_move": expected_move,
            "skew": skew,
            "iv_regime": _regime(iv_rank, config),
        })

    return pd.DataFrame(rows)


def _delta_iv(side: pd.DataFrame, target_delta: float) -> float:
    if side.empty:
        return np.nan
    s = side.copy()
    s["dd"] = (s["delta"] - target_delta).abs()
    return float(s.sort_values("dd").iloc[0]["implied_volatility"])
