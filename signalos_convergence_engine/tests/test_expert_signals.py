"""Tests for expert signals (revisions/insider/squeeze) + Power Gauge blending."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.config import DEFAULT_CONFIG
from signalos.data_sources.expert_data import make_demo_expert, validate_expert
from signalos.features.expert_signals import (
    revision_score, insider_score, squeeze_score, compute_expert_signals,
)
from signalos.scoring.chaikin_power_gauge import experts_bucket
from signalos.trade_construction.options_screens import classify_screen


def test_score_bounds_and_monotonic():
    assert revision_score(0.40) > revision_score(0.0) > revision_score(-0.10)
    assert insider_score(1.0) == 100 and insider_score(-1.0) == 0 and insider_score(0.0) == 50
    assert squeeze_score(0.30, 10) > squeeze_score(0.05, 1)
    assert 0 <= squeeze_score(0.20, 6) <= 100


def test_compute_expert_signals_columns():
    out = compute_expert_signals(make_demo_expert())
    assert set(["ticker", "revision_score", "insider_score", "squeeze_score"]).issubset(out.columns)
    nvda = out[out["ticker"] == "NVDA"].iloc[0]
    assert nvda["revision_score"] > 50      # compounder demo names get up-revisions


def test_experts_bucket_backward_compatible_without_signals():
    # No revision/insider columns -> flow-only value, unchanged behavior.
    row = pd.Series({"ask_side_ratio": 0.8, "repeat_flow_score": 0.8, "catalyst_score": 80})
    flow_only = experts_bucket(row)
    assert 75 <= flow_only <= 85


def test_experts_bucket_blends_when_signals_present():
    base = pd.Series({"ask_side_ratio": 0.8, "repeat_flow_score": 0.8, "catalyst_score": 80})
    boosted = base.copy()
    boosted["revision_score"] = 100.0
    boosted["insider_score"] = 100.0
    weak = base.copy()
    weak["revision_score"] = 0.0
    weak["insider_score"] = 0.0
    assert experts_bucket(weak) < experts_bucket(base) < experts_bucket(boosted) + 1e-6


def test_squeeze_screen_fires():
    row = pd.Series({
        "bias": "Bullish", "power_gauge_rating": "Neutral", "capital_verdict": "Neutral",
        "iv_regime": "Normal", "uoa_score": 80, "money_flow_score": 60, "squeeze_score": 75,
    })
    assert classify_screen(row, DEFAULT_CONFIG) == "SQUEEZE"


def test_squeeze_blocked_when_gauge_bearish():
    row = pd.Series({
        "bias": "Bullish", "power_gauge_rating": "Bearish", "capital_verdict": "Neutral",
        "iv_regime": "Normal", "uoa_score": 80, "money_flow_score": 60, "squeeze_score": 90,
    })
    assert classify_screen(row, DEFAULT_CONFIG) != "SQUEEZE"
