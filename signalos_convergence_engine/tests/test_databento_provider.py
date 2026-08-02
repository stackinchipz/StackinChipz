"""Tests for the Databento OPRA flow features (network-free pure functions)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.data_sources.databento_provider import (
    classify_trade_side, compute_flow_features, enrich_option_chain,
    DatabentoOptionsProvider,
)


# --- Quote-rule classification ---
def test_classify_trade_side_quote_rule():
    assert classify_trade_side(1.05, 1.00, 1.05) == "ask"    # at ask
    assert classify_trade_side(1.10, 1.00, 1.05) == "ask"    # through ask
    assert classify_trade_side(1.00, 1.00, 1.05) == "bid"    # at bid
    assert classify_trade_side(1.04, 1.00, 1.05) == "ask"    # above mid
    assert classify_trade_side(1.01, 1.00, 1.05) == "bid"    # below mid
    assert classify_trade_side(1.025, 1.00, 1.05) == "mid"   # exactly mid


def test_classify_trade_side_handles_bad_quotes():
    assert classify_trade_side(1.0, np.nan, 1.05) == "mid"
    assert classify_trade_side(1.0, 1.10, 1.00) == "mid"     # crossed book
    assert classify_trade_side(np.nan, 1.0, 1.05) == "mid"


def _tape(rows):
    return pd.DataFrame(rows)


def _t(sym, ts, price, size, bid, ask, pub=1):
    return {"symbol": sym, "ts_event": ts, "price": price, "size": size,
            "bid_px_00": bid, "ask_px_00": ask, "publisher_id": pub}


# --- Ask-side ratio (the field that was a hardcoded constant) ---
def test_ask_side_ratio_all_buyer_initiated():
    tape = _tape([_t("AAPL_C", f"2026-06-01T14:{m:02d}:00Z", 2.05, 100, 2.00, 2.05)
                  for m in range(5)])
    f = compute_flow_features(tape).iloc[0]
    assert f["ask_side_ratio"] == 1.0


def test_ask_side_ratio_all_seller_initiated():
    tape = _tape([_t("AAPL_C", f"2026-06-01T14:{m:02d}:00Z", 2.00, 100, 2.00, 2.05)
                  for m in range(5)])
    f = compute_flow_features(tape).iloc[0]
    assert f["ask_side_ratio"] == 0.0


def test_ask_side_ratio_is_premium_weighted():
    # One huge buy vs many tiny sells -> ratio should lean buyer-initiated.
    tape = _tape(
        [_t("X", "2026-06-01T14:00:00Z", 2.05, 1000, 2.00, 2.05)] +
        [_t("X", f"2026-06-01T14:0{m}:00Z", 2.00, 10, 2.00, 2.05) for m in range(1, 6)]
    )
    f = compute_flow_features(tape).iloc[0]
    assert f["ask_side_ratio"] > 0.9


def test_premium_and_counts():
    tape = _tape([_t("X", "2026-06-01T14:00:00Z", 2.00, 10, 1.95, 2.05)])
    f = compute_flow_features(tape).iloc[0]
    assert f["premium_traded"] == 2.00 * 10 * 100      # contract multiplier
    assert f["trade_count"] == 1 and f["tape_volume"] == 10


# --- Repeat flow: sustained accumulation beats one-and-done ---
def test_repeat_flow_rewards_persistence():
    spread = _tape([_t("A", f"2026-06-01T14:{m:02d}:00Z", 2.05, 50, 2.00, 2.05)
                    for m in range(20)])
    single = _tape([_t("B", "2026-06-01T14:00:00Z", 2.05, 1000, 2.00, 2.05)])
    a = compute_flow_features(spread).iloc[0]["repeat_flow_score"]
    b = compute_flow_features(single).iloc[0]["repeat_flow_score"]
    assert a > b
    assert 0.0 <= b < 0.2


# --- Sweep detection: same contract, many venues, tight window ---
def test_sweep_score_detects_multi_venue_burst():
    ts = "2026-06-01T14:00:00.100Z"
    sweep = _tape([_t("A", ts, 2.05, 100, 2.00, 2.05, pub=v) for v in (1, 2, 3, 4)])
    single_venue = _tape([_t("B", ts, 2.05, 100, 2.00, 2.05, pub=1) for _ in range(4)])
    assert compute_flow_features(sweep).iloc[0]["sweep_score"] == 1.0
    assert compute_flow_features(single_venue).iloc[0]["sweep_score"] == 0.0


def test_empty_tape_safe():
    out = compute_flow_features(pd.DataFrame())
    assert out.empty and "ask_side_ratio" in out.columns


# --- Chain enrichment ---
def test_enrich_replaces_placeholders_and_keeps_uncovered():
    chain = pd.DataFrame([
        {"option_symbol": "COVERED", "ask_side_ratio": 0.55, "repeat_flow_score": 0.50,
         "avg_contract_volume_20d": 50},
        {"option_symbol": "UNCOVERED", "ask_side_ratio": 0.55, "repeat_flow_score": 0.50,
         "avg_contract_volume_20d": 50},
    ])
    flow = pd.DataFrame([{"option_symbol": "COVERED", "ask_side_ratio": 0.92,
                          "repeat_flow_score": 0.80, "sweep_score": 0.4,
                          "premium_traded": 1_000_000.0}])
    base = pd.DataFrame([{"option_symbol": "COVERED", "avg_contract_volume_20d": 275.0}])
    out = enrich_option_chain(chain, flow, base).set_index("option_symbol")

    assert out.loc["COVERED", "ask_side_ratio"] == 0.92        # real tape value
    assert out.loc["COVERED", "avg_contract_volume_20d"] == 275.0
    assert out.loc["UNCOVERED", "ask_side_ratio"] == 0.55      # placeholder preserved
    assert out.loc["UNCOVERED", "avg_contract_volume_20d"] == 50


def test_enrich_noop_without_flow():
    chain = pd.DataFrame([{"option_symbol": "X", "ask_side_ratio": 0.55}])
    assert enrich_option_chain(chain, pd.DataFrame()).equals(chain)


def test_parent_symbology_format():
    assert DatabentoOptionsProvider.parent_symbols(["aapl", "NVDA"]) == ["AAPL.OPT", "NVDA.OPT"]
