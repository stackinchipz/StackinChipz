"""Tests for the options P&L backtest."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.backtest.options_pnl import (
    bs_price, backtest_option_pnl, compare_strategies, BacktestConfig,
)


def test_bs_price_monotonic_and_parity():
    c = bs_price(100, 100, 0.5, 0.3, "call")
    p = bs_price(100, 100, 0.5, 0.3, "put")
    assert c > 0 and p > 0
    # Calls rise with spot.
    assert bs_price(110, 100, 0.5, 0.3, "call") > c
    # Put-call parity: C - P == S - K*exp(-rT).
    parity = c - p
    expected = 100 - 100 * np.exp(-0.04 * 0.5)
    assert abs(parity - expected) < 0.5


def test_bs_intrinsic_at_expiry():
    assert abs(bs_price(120, 100, 0.0, 0.3, "call") - 20.0) < 1e-6
    assert bs_price(80, 100, 0.0, 0.3, "call") == 0.0


def _two_signals():
    return pd.DataFrame([
        {"ticker": "UP", "type": "call", "bias": "Bullish", "decision": "Tradable",
         "strike": 100, "implied_volatility": 0.40, "days_to_expiration": 60,
         "spread_pct": 0.06, "date": "2025-01-02", "convergence_score": 80,
         "capital_verdict": "Compounder", "suggested_structure": "Long call"},
        {"ticker": "DN", "type": "put", "bias": "Bearish", "decision": "Tradable",
         "strike": 100, "implied_volatility": 0.40, "days_to_expiration": 60,
         "spread_pct": 0.06, "date": "2025-01-02", "convergence_score": 80,
         "capital_verdict": "Capital Destroyer", "suggested_structure": "Long put"},
    ])


def _stock_path():
    dates = pd.bdate_range("2025-01-02", periods=40)
    up = pd.DataFrame({"date": dates, "ticker": "UP",
                       "close": np.linspace(100, 130, len(dates))})
    dn = pd.DataFrame({"date": dates, "ticker": "DN",
                       "close": np.linspace(100, 80, len(dates))})
    return pd.concat([up, dn], ignore_index=True)


def test_long_call_profits_when_underlying_rises():
    trades, summary = backtest_option_pnl(_two_signals(), _stock_path(),
                                          BacktestConfig(horizon_days=20, target_pct=5, stop_pct=0.9))
    up = trades[trades["ticker"] == "UP"].iloc[0]
    dn = trades[trades["ticker"] == "DN"].iloc[0]
    assert up["option_return"] > 0      # call wins on a +30% move
    assert dn["option_return"] > 0      # put wins on a -20% move
    assert summary.iloc[0]["num_trades"] == 2


def test_iv_crush_hurts_long_premium():
    base, _ = backtest_option_pnl(_two_signals(), _stock_path(),
                                  BacktestConfig(horizon_days=20, target_pct=5, stop_pct=0.95))
    crush, _ = backtest_option_pnl(_two_signals(), _stock_path(),
                                   BacktestConfig(horizon_days=20, target_pct=5, stop_pct=0.95,
                                                  iv_shock=-0.20))
    assert crush["option_return"].mean() < base["option_return"].mean()


def test_compare_strategies_returns_three_rows():
    comp = compare_strategies(_two_signals(), _stock_path(), BacktestConfig(target_pct=5, stop_pct=0.95))
    assert set(comp["strategy"]) == {"Flow-only", "Convergence>=70", "Convergence+Fundamental"}
