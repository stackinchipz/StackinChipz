"""Pure data helpers for the screen dashboard.

Kept free of Streamlit so they're unit-testable. The Streamlit app
(`app/screen_dashboard.py`) is a thin rendering layer over these.
"""
from __future__ import annotations

import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG
from signalos.pipeline_screen import size_screen
from signalos.agent import run_agent


OVERVIEW_COLS = [
    "ticker", "bias", "decision", "screen", "convergence_score",
    "power_gauge_rating", "capital_verdict", "capital_efficiency_score",
    "iv_regime", "screen_structure",
]


def screen_overview(signals: pd.DataFrame, top: int = 50) -> pd.DataFrame:
    """Top-ranked one-row-per-contract overview for the main table."""
    if signals is None or signals.empty:
        return pd.DataFrame(columns=OVERVIEW_COLS)
    cols = [c for c in OVERVIEW_COLS if c in signals.columns]
    return signals[cols].head(top).reset_index(drop=True)


def screen_by_pattern(signals: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Group qualifying rows by named screen (Compounder/Destroyer/Squeeze/...)."""
    if signals is None or signals.empty or "screen" not in signals.columns:
        return {}
    out = {}
    for name, g in signals[signals["screen"].astype(str) != ""].groupby("screen"):
        cols = [c for c in OVERVIEW_COLS if c in g.columns]
        out[str(name)] = g[cols].reset_index(drop=True)
    return out


def book_summary(signals: pd.DataFrame, config: ScannerConfig = DEFAULT_CONFIG) -> dict:
    """Run the risk engine and return the book-level heat + net Greeks."""
    sized = size_screen(signals, config)
    if sized is None or sized.empty:
        return {"positions": 0, "open_risk": 0.0, "heat_pct": 0.0,
                "net_delta": 0.0, "net_gamma": 0.0, "net_theta": 0.0, "net_vega": 0.0}
    return dict(sized.attrs.get("book", {}))


def proposal_cards(signals: pd.DataFrame, config: ScannerConfig = DEFAULT_CONFIG,
                   limit: int = 20) -> list[dict]:
    """Propose-only agent output as render-ready cards (thesis + invalidation)."""
    out = run_agent(signals, config)
    cards = [r for r in out["proposals"] if r.get("contracts", 0) > 0]
    return cards[:limit]
