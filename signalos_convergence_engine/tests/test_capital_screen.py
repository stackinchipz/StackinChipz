"""Tests for the new capital-efficiency / IV-regime / risk / screen modules."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.config import DEFAULT_CONFIG
from signalos.data_sources.fundamentals import make_demo_fundamentals, validate_fundamentals
from signalos.features.capital_efficiency import compute_capital_efficiency
from signalos.features.iv_regime import compute_iv_regime
from signalos.scoring.capital_efficiency_score import add_capital_efficiency_scores
from signalos.scoring.chaikin_power_gauge import power_gauge_score, power_gauge_rating
from signalos.risk import size_position, aggregate_book_greeks, RiskState
from signalos.trade_construction.options_screens import suggest_trade


def _company(ticker, **trajectory):
    """Build a 5-year fundamentals frame from simple yearly dicts."""
    rows = []
    for i, year in enumerate(range(2020, 2025)):
        rows.append({"ticker": ticker, "fiscal_year": year, "period_end": f"{year}-12-31",
                     **{k: v[i] for k, v in trajectory.items()}})
    return validate_fundamentals(pd.DataFrame(rows))


def test_compounder_detected():
    # Rising revenue, expanding margins, heavy productive capex.
    g = _company(
        "GOOD",
        revenue=[1000, 1250, 1560, 1950, 2440],
        operating_income=[150, 200, 270, 360, 490],
        net_income=[110, 150, 205, 275, 380],
        total_assets=[1500, 1700, 1950, 2250, 2600],
        total_equity=[800, 920, 1080, 1280, 1520],
        total_debt=[300, 320, 350, 380, 410],
        cash=[100, 120, 140, 160, 190],
        capex=[120, 160, 215, 290, 390],
        depreciation_amortization=[70, 85, 105, 130, 160],
        rd_expense=[80, 100, 130, 165, 210],
        goodwill=[0, 0, 0, 0, 0],
        shares_diluted=[500] * 5,
    )
    m = add_capital_efficiency_scores(compute_capital_efficiency(g, DEFAULT_CONFIG))
    row = m.iloc[0]
    assert row["capital_verdict"] == "Compounder"
    assert row["roiic"] > DEFAULT_CONFIG.cost_of_capital
    assert row["capital_efficiency_score"] > 60


def test_capital_destroyer_detected():
    # Heavy capex but flat revenue and compressing margins -> low/neg ROIIC.
    g = _company(
        "BADC",
        revenue=[2000, 2010, 1990, 2005, 1995],
        operating_income=[300, 270, 230, 190, 150],
        net_income=[220, 200, 170, 140, 110],
        total_assets=[3000, 3300, 3600, 3950, 4300],
        total_equity=[1500, 1550, 1600, 1650, 1700],
        total_debt=[800, 950, 1100, 1300, 1500],
        cash=[150, 150, 150, 150, 150],
        capex=[200, 260, 330, 420, 540],
        depreciation_amortization=[150, 170, 190, 210, 230],
        rd_expense=[0, 0, 0, 0, 0],
        goodwill=[600, 600, 600, 600, 600],
        shares_diluted=[400] * 5,
    )
    m = add_capital_efficiency_scores(compute_capital_efficiency(g, DEFAULT_CONFIG))
    row = m.iloc[0]
    assert row["capital_verdict"] == "Capital Destroyer"
    assert row["roiic"] < DEFAULT_CONFIG.destroyer_max_roiic


def test_uniform_vs_gaap_distortion_recorded():
    g = make_demo_fundamentals().query("ticker == 'NVDA'")
    m = compute_capital_efficiency(g, DEFAULT_CONFIG)
    assert "accounting_distortion" in m.columns
    assert pd.notna(m.iloc[0]["uniform_roa"])


def test_iv_regime_labels_and_rank():
    chain = pd.DataFrame([
        {"ticker": "AAA", "type": "call", "strike": 100, "delta": 0.5, "mid": 5.0,
         "implied_volatility": 0.30, "days_to_expiration": 30},
        {"ticker": "AAA", "type": "put", "strike": 100, "delta": -0.5, "mid": 4.5,
         "implied_volatility": 0.32, "days_to_expiration": 30},
        {"ticker": "BBB", "type": "call", "strike": 50, "delta": 0.5, "mid": 6.0,
         "implied_volatility": 0.95, "days_to_expiration": 30},
        {"ticker": "BBB", "type": "put", "strike": 50, "delta": -0.5, "mid": 6.5,
         "implied_volatility": 0.98, "days_to_expiration": 30},
    ])
    ivr = compute_iv_regime(chain, None, DEFAULT_CONFIG).set_index("ticker")
    assert ivr.loc["BBB", "iv_rank"] > ivr.loc["AAA", "iv_rank"]
    assert ivr.loc["AAA", "expected_move"] > 0


def test_position_sizing_respects_risk_cap():
    state = RiskState(account_size=100_000)
    row = pd.Series({"decision": "Tradable", "suggested_structure": "Long call",
                     "mid": 2.00, "sector": "Tech"})
    s = size_position(row, state, DEFAULT_CONFIG)
    # 1% of 100k = $1000 budget; long call max-loss = $200/contract -> 5 contracts.
    assert s["contracts"] == 5
    assert s["dollar_risk"] <= 100_000 * DEFAULT_CONFIG.max_risk_per_trade_pct + 1e-6


def test_portfolio_heat_kill_switch():
    state = RiskState(account_size=100_000, day_pnl_pct=-0.05)  # past -4% kill
    row = pd.Series({"decision": "A+ setup", "suggested_structure": "Long call",
                     "mid": 1.00, "sector": "Tech"})
    s = size_position(row, state, DEFAULT_CONFIG)
    assert s["contracts"] == 0
    assert "kill-switch" in (s["binding_constraint"] or "")


def test_book_greeks_sign_by_type():
    positions = pd.DataFrame([
        {"contracts": 10, "type": "call", "delta": 0.5, "gamma": 0.02, "theta": -0.05, "vega": 0.1},
        {"contracts": 10, "type": "put", "delta": -0.5, "gamma": 0.02, "theta": -0.05, "vega": 0.1},
    ])
    g = aggregate_book_greeks(positions)
    # Long call (+delta) and long put (-delta) of equal size roughly net to 0.
    assert abs(g["net_delta"]) < 1e-6
    assert g["net_vega"] > 0  # both long premium -> long vega


def test_power_gauge_bullish_for_strong_fundamentals():
    row = pd.Series({
        "uniform_roa": 0.25, "roiic": 0.30, "uniform_roa_trend": 0.05,
        "revenue_cagr": 0.25, "op_margin_trend": 0.03, "incr_op_margin": 0.30,
        "money_flow_score": 85, "trend_score": 80, "rs_score": 80,
        "ask_side_ratio": 0.8, "repeat_flow_score": 0.8, "catalyst_score": 80,
    })
    score = power_gauge_score(row, DEFAULT_CONFIG)
    assert score >= 65
    assert power_gauge_rating(score) == "Bullish"


def test_suggest_trade_regime_aware():
    # High IV -> should propose a credit (premium-selling) structure.
    row = pd.Series({"bias": "Bullish", "power_gauge_rating": "Bullish",
                     "capital_verdict": "Compounder", "iv_regime": "High",
                     "uoa_score": 80, "money_flow_score": 75, "spread_pct": 0.05,
                     "days_to_expiration": 30, "strike": 100, "expiration": "2026-01-01",
                     "expected_move": 0.06})
    t = suggest_trade(row, DEFAULT_CONFIG)
    assert "credit" in t["structure"].lower()
