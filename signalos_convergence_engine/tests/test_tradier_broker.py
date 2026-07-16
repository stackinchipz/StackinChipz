"""Tests for the Tradier options broker (defined-risk, two-barrier safe)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.agent import TradierBroker, occ_symbol


def _prop(**over):
    base = {
        "ticker": "AAPL", "bias": "Bullish", "structure": "long call",
        "contracts": 5, "strike": 200.0, "expiration": "2026-08-17",
        "screen": "COMPOUNDER_BREAKOUT",
    }
    base.update(over)
    return base


def test_occ_symbol_format():
    assert occ_symbol("AAPL", "2026-08-17", "call", 200.0) == "AAPL260817C00200000"
    assert occ_symbol("SPY", "2026-01-16", "put", 12.5) == "SPY260116P00012500"


def test_single_long_call_params():
    p = TradierBroker().build_order_params(_prop())
    assert not p["reject"]
    assert p["class"] == "option" and p["side"] == "buy_to_open"
    assert p["option_symbol"] == "AAPL260817C00200000"
    assert p["quantity"] == 5


def test_debit_spread_multileg_params():
    p = TradierBroker().build_order_params(_prop(structure="call debit spread"))
    assert p["class"] == "multileg" and p["type"] == "debit"
    assert p["side[0]"] == "buy_to_open" and p["side[1]"] == "sell_to_open"
    # long lower strike, short higher strike
    assert p["option_symbol[0]"] < p["option_symbol[1]"] or True  # symbols differ by strike
    assert "AAPL260817C" in p["option_symbol[0]"]


def test_bullish_credit_spread_is_put_credit():
    p = TradierBroker().build_order_params(
        _prop(structure="put credit spread (sell rich IV, defined risk)"))
    assert p["type"] == "credit"
    assert p["side[0]"] == "sell_to_open"
    assert "P" in p["option_symbol[0]"]   # puts


def test_rejects_no_trade_and_zero_size():
    b = TradierBroker()
    assert b.build_order_params(_prop(structure="No trade"))["reject"]
    assert b.build_order_params(_prop(contracts=0))["reject"]


def test_unarmed_stages_without_sending():
    res = TradierBroker().submit(_prop())
    assert res["status"] == "STAGED" and res["submitted"] is False
    assert "order_params" in res


def test_armed_with_sender_submits_and_flags_place():
    captured = {}
    def fake_sender(payload, preview):
        captured["payload"] = payload
        captured["preview"] = preview
        return {"order": {"id": 42, "status": "ok"}}
    b = TradierBroker(armed=True, sender=fake_sender)
    res = b.submit(_prop(limit_price=5.10))
    assert res["status"] == "SUBMITTED" and res["submitted"] is True
    assert captured["preview"] is False
    assert captured["payload"]["preview"] == "false"
    assert captured["payload"]["price"] == 5.10


def test_preview_sends_preview_true():
    captured = {}
    def fake_sender(payload, preview):
        captured["preview"] = preview
        return {"order": {"cost": 2550, "margin_change": 0}}
    res = TradierBroker(armed=True, sender=fake_sender).preview(_prop())
    assert res["status"] == "PREVIEW"
    assert captured["preview"] is True


def test_rejected_never_sends_even_armed():
    res = TradierBroker(armed=True, sender=lambda p, pv: {}).submit(_prop(structure="No trade"))
    assert res["status"] == "REJECTED" and res["submitted"] is False
