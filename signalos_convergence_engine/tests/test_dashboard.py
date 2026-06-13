"""Tests for the dashboard data helpers (Streamlit-free)."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.reporting import (
    screen_overview, screen_by_pattern, book_summary, proposal_cards,
)


def _signals():
    return pd.DataFrame([
        {"ticker": "PLTR", "bias": "Bullish", "decision": "Tradable",
         "screen": "COMPOUNDER_BREAKOUT", "screen_structure": "long call",
         "suggested_structure": "Long call", "screen_entry_note": "Compounder Breakout",
         "convergence_score": 82, "power_gauge_rating": "Bullish",
         "capital_verdict": "Compounder", "capital_efficiency_score": 57,
         "iv_regime": "Low", "mid": 4.0, "sector": "Technology", "type": "call",
         "delta": 0.55, "gamma": 0.02, "theta": -0.04, "vega": 0.2,
         "uoa_score": 90, "money_flow_score": 75},
        {"ticker": "BMY", "bias": "Bearish", "decision": "Tradable",
         "screen": "DESTROYER_BREAKDOWN", "screen_structure": "put debit spread",
         "suggested_structure": "Put debit spread", "screen_entry_note": "Destroyer Breakdown",
         "convergence_score": 71, "power_gauge_rating": "Bearish",
         "capital_verdict": "Capital Destroyer", "capital_efficiency_score": 11,
         "iv_regime": "Extreme", "mid": 3.0, "sector": "Healthcare", "type": "put",
         "delta": -0.45, "gamma": 0.02, "theta": -0.03, "vega": 0.15,
         "uoa_score": 85, "money_flow_score": 78},
    ])


def test_screen_overview_returns_columns():
    ov = screen_overview(_signals())
    assert "power_gauge_rating" in ov.columns
    assert len(ov) == 2


def test_screen_by_pattern_groups():
    pats = screen_by_pattern(_signals())
    assert set(pats) == {"COMPOUNDER_BREAKOUT", "DESTROYER_BREAKDOWN"}
    assert len(pats["COMPOUNDER_BREAKOUT"]) == 1


def test_book_summary_has_greeks():
    book = book_summary(_signals())
    assert "net_vega" in book and "positions" in book
    assert book["positions"] >= 1


def test_proposal_cards_have_narrative():
    cards = proposal_cards(_signals())
    assert cards
    assert all("thesis" in c and "invalidation" in c for c in cards)


def test_empty_inputs_safe():
    assert screen_overview(pd.DataFrame()).empty
    assert screen_by_pattern(pd.DataFrame()) == {}
