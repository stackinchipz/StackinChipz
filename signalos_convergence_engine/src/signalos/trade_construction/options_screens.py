"""Special options screens + IV-regime-aware trade suggestions.

Each screen is a named pattern that fires when flow, the Power Gauge, capital
efficiency, and the IV regime line up. The structure is chosen by IV regime so
the book isn't always paying up for premium:

    Low IV    -> long calls/puts or debit spreads (cheap premium, buy convexity)
    High IV   -> defined-risk credit (spreads) to be a net premium SELLER
    Extreme   -> tighten / favor credit, smaller size
    Earnings within block window -> no long premium (IV-crush guard)

Screens implemented:
    COMPOUNDER_BREAKOUT  - bullish gauge + Compounder + bullish flow
    DESTROYER_BREAKDOWN  - bearish gauge + Capital Destroyer + bearish flow
    PREMIUM_REVERSION    - rich IV (sell premium, defined risk)
    FLOW_CONVERGENCE     - classic UOA + money-flow convergence (fundamental-agnostic)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG


def _structure_for_regime(bias: str, iv_regime: str, dte: float,
                          earnings_dte: float | None, config: ScannerConfig) -> str:
    long_side = "call" if bias == "Bullish" else "put"

    # Earnings IV-crush guard: never hold naked long premium into the print.
    if earnings_dte is not None and not pd.isna(earnings_dte) and 0 <= earnings_dte <= config.earnings_block_dte:
        return f"{long_side} debit spread (earnings IV-crush guard)"

    if iv_regime in {"High", "Extreme"}:
        # Be a net premium seller with defined risk.
        credit = "put credit spread" if bias == "Bullish" else "call credit spread"
        return f"{credit} (sell rich IV, defined risk)"

    if iv_regime == "Low" and (pd.isna(dte) or dte >= 21):
        return f"long {long_side} (cheap IV) or {long_side} debit spread"

    return f"{long_side} debit spread"


def classify_screen(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> str:
    bias = row.get("bias", "")
    rating = str(row.get("power_gauge_rating", ""))
    verdict = str(row.get("capital_verdict", ""))
    iv_regime = str(row.get("iv_regime", ""))
    uoa = float(row.get("uoa_score", 0) or 0)
    mf = float(row.get("money_flow_score", 0) or 0)

    if (bias == "Bullish" and rating.startswith("Bullish")
            and verdict in {"Compounder", "Quality"} and uoa >= config.min_uoa_score):
        return "COMPOUNDER_BREAKOUT"

    if (bias == "Bearish" and rating.startswith("Bearish")
            and verdict == "Capital Destroyer" and uoa >= config.min_uoa_score):
        return "DESTROYER_BREAKDOWN"

    if iv_regime in {"High", "Extreme"} and uoa >= config.min_uoa_score and mf >= 50:
        return "PREMIUM_REVERSION"

    if uoa >= config.min_uoa_score and mf >= config.min_money_flow_score:
        return "FLOW_CONVERGENCE"

    return ""


def suggest_trade(row: pd.Series, config: ScannerConfig = DEFAULT_CONFIG) -> dict:
    """Concrete, regime-aware trade suggestion for one candidate."""
    screen = classify_screen(row, config)
    bias = row.get("bias", "")
    iv_regime = str(row.get("iv_regime", "Unknown"))
    dte = float(row.get("days_to_expiration", np.nan) or np.nan)
    earnings_dte = row.get("earnings_dte", np.nan)
    spread_pct = float(row.get("spread_pct", 1.0) or 1.0)

    if not screen or bias not in {"Bullish", "Bearish"}:
        return {"screen": "", "structure": "No trade", "entry_note": "No qualifying pattern"}

    if spread_pct > config.max_option_spread_pct:
        return {"screen": screen, "structure": "No trade", "entry_note": "Option spread too wide"}

    structure = _structure_for_regime(bias, iv_regime, dte, earnings_dte, config)

    strike = row.get("strike")
    expiration = row.get("expiration")
    expected_move = row.get("expected_move")
    em_txt = f"~{expected_move*100:.1f}% expected move" if pd.notna(expected_move) else "expected move n/a"

    entry_note = (
        f"{screen.replace('_', ' ').title()} | {structure} | "
        f"ref strike {strike}, exp {expiration} | IV {iv_regime}, {em_txt}"
    )
    return {"screen": screen, "structure": structure, "entry_note": entry_note}


def add_options_screens(df: pd.DataFrame, config: ScannerConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    out = df.copy()
    suggestions = out.apply(lambda r: suggest_trade(r, config), axis=1, result_type="expand")
    out["screen"] = suggestions["screen"]
    out["screen_structure"] = suggestions["structure"]
    out["screen_entry_note"] = suggestions["entry_note"]
    return out
