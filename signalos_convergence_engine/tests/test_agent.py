"""Tests for the propose-only agent execution layer."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.agent import run_agent, DryRunBroker, MCPBrokerStub
from signalos.agent.proposals import build_proposals


def _signals():
    return pd.DataFrame([
        {"ticker": "PLTR", "bias": "Bullish", "decision": "Tradable",
         "suggested_structure": "Long call", "screen_structure": "long call",
         "screen": "COMPOUNDER_BREAKOUT", "screen_entry_note": "Compounder Breakout | long call",
         "mid": 4.0, "sector": "Technology", "type": "call",
         "delta": 0.55, "gamma": 0.02, "theta": -0.04, "vega": 0.2,
         "convergence_score": 82, "power_gauge_rating": "Bullish",
         "capital_verdict": "Compounder", "iv_regime": "Low",
         "uoa_score": 90, "money_flow_score": 75, "uniform_roa": 0.16, "roiic": 0.19},
        {"ticker": "BMY", "bias": "Bearish", "decision": "Tradable",
         "suggested_structure": "Put debit spread", "screen_structure": "put debit spread",
         "screen": "DESTROYER_BREAKDOWN", "screen_entry_note": "Destroyer Breakdown",
         "mid": 3.0, "sector": "Healthcare", "type": "put",
         "delta": -0.45, "gamma": 0.02, "theta": -0.03, "vega": 0.15,
         "convergence_score": 71, "power_gauge_rating": "Bearish",
         "capital_verdict": "Capital Destroyer", "iv_regime": "Extreme",
         "uoa_score": 85, "money_flow_score": 78, "roiic": 0.02},
    ])


def test_agent_is_propose_only_by_default():
    out = run_agent(_signals())
    assert out["proposals"]
    for r in out["proposals"]:
        # Default path never submits.
        assert r["routing"]["status"] in {"PROPOSED", "SKIPPED"}
        assert r["routing"].get("submitted", False) is False


def test_proposals_have_thesis_and_invalidation():
    props = build_proposals(_signals())
    assert len(props) == 2
    for p in props:
        assert p.thesis and p.invalidation
        assert p.status == "PROPOSED"
    pltr = next(p for p in props if p.ticker == "PLTR")
    assert "Compounder" in pltr.thesis
    assert "20DMA" in pltr.invalidation


def test_dry_run_broker_never_submits_even_when_execute_true():
    out = run_agent(_signals(), broker=DryRunBroker(), execute=True)
    for r in out["proposals"]:
        if r["contracts"] > 0:
            assert r["routing"]["status"] == "DRY_RUN"
            assert r["routing"]["submitted"] is False


def test_mcp_broker_stub_refuses_to_submit():
    with pytest.raises(NotImplementedError):
        MCPBrokerStub().submit({"ticker": "X", "contracts": 1})


def test_book_summary_present():
    out = run_agent(_signals())
    assert "positions" in out["book"]
    assert "net_vega" in out["book"]
