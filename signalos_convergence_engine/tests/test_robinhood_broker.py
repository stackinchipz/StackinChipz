"""Tests for the Robinhood MCP broker scaffold (defined-risk, two-barrier safe)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.agent import RobinhoodMCPBroker


def _prop(**over):
    base = {
        "ticker": "PLTR", "bias": "Bullish", "structure": "long call",
        "contracts": 5, "strike": 200.0, "expiration": "2026-08-17",
        "dollar_risk": 900.0, "screen": "COMPOUNDER_BREAKOUT", "thesis": "...",
    }
    base.update(over)
    return base


def test_single_long_call_spec():
    spec = RobinhoodMCPBroker().build_order_spec(_prop())
    assert not spec["reject"]
    assert spec["order_class"] == "option"
    assert len(spec["legs"]) == 1
    leg = spec["legs"][0]
    assert leg["action"] == "buy_to_open" and leg["option_type"] == "call"
    assert spec["defined_risk"] is True


def test_debit_spread_two_legs():
    spec = RobinhoodMCPBroker().build_order_spec(_prop(structure="call debit spread"))
    assert len(spec["legs"]) == 2
    assert spec["order_class"] == "multileg"
    actions = {l["action"] for l in spec["legs"]}
    assert actions == {"buy_to_open", "sell_to_open"}
    # Long lower strike, short higher strike for a bull call spread.
    longs = [l for l in spec["legs"] if l["action"] == "buy_to_open"][0]
    shorts = [l for l in spec["legs"] if l["action"] == "sell_to_open"][0]
    assert shorts["strike"] > longs["strike"]


def test_bullish_credit_spread_is_put_credit():
    spec = RobinhoodMCPBroker().build_order_spec(
        _prop(structure="put credit spread (sell rich IV, defined risk)"))
    sold = [l for l in spec["legs"] if l["action"] == "sell_to_open"][0]
    bought = [l for l in spec["legs"] if l["action"] == "buy_to_open"][0]
    assert sold["option_type"] == "put"
    assert bought["strike"] < sold["strike"]   # protective wing further OTM


def test_rejects_no_trade_and_zero_size():
    assert RobinhoodMCPBroker().build_order_spec(_prop(structure="No trade"))["reject"]
    assert RobinhoodMCPBroker().build_order_spec(_prop(contracts=0))["reject"]


def test_unarmed_stages_without_sending():
    res = RobinhoodMCPBroker().submit(_prop())
    assert res["status"] == "STAGED"
    assert res["submitted"] is False
    assert "order_spec" in res


def test_armed_without_invoker_raises():
    with pytest.raises(NotImplementedError):
        RobinhoodMCPBroker(armed=True).submit(_prop())


def test_armed_with_invoker_submits():
    captured = {}
    def fake_invoker(spec):
        captured["spec"] = spec
        return {"order_id": "RH-123", "state": "accepted"}
    res = RobinhoodMCPBroker(armed=True, mcp_invoker=fake_invoker).submit(_prop())
    assert res["status"] == "SUBMITTED" and res["submitted"] is True
    assert res["result"]["order_id"] == "RH-123"
    assert captured["spec"]["underlying"] == "PLTR"


def test_rejected_proposal_never_submits_even_when_armed():
    res = RobinhoodMCPBroker(armed=True, mcp_invoker=lambda s: {}).submit(_prop(structure="No trade"))
    assert res["status"] == "REJECTED" and res["submitted"] is False
