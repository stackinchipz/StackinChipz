"""Tradier options broker — places the defined-risk structures the screen builds.

Unlike Robinhood's equities-only beta, Tradier can trade options today, using the
same token that already feeds your chains. This broker turns a proposal into
Tradier order form params (single-leg or multileg spread, with OCC option
symbols) and, when armed, posts them.

Safety mirrors the other brokers — two independent barriers before anything
sends:
  1. constructed with `armed=True`, AND
  2. a real token+account (or an injected `sender` for tests).
Default construction STAGES the order (returns params, sends nothing). Naked /
no-trade / zero-size structures are rejected even when armed. Use `preview()`
(Tradier preview=true) before placing — the analogue of RH's review-before-place.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
import requests

LIVE_BASE_URL = "https://api.tradier.com/v1"
SANDBOX_BASE_URL = "https://sandbox.tradier.com/v1"


@dataclass
class TradierBroker:
    token: str | None = None
    account_id: str | None = None
    sandbox: bool = False
    armed: bool = False
    spread_width_pct: float = 0.05
    duration: str = "day"
    sender: Callable[[dict, bool], dict] | None = None   # (params, preview) -> result; for tests/local wiring
    timeout: int = 30
    name: str = field(default="tradier", init=False)

    @property
    def base_url(self) -> str:
        return SANDBOX_BASE_URL if self.sandbox else LIVE_BASE_URL

    # --- Order construction (defined-risk only) ---------------------------
    def build_order_params(self, proposal: dict) -> dict:
        structure = str(proposal.get("structure", "")).lower()
        bias = str(proposal.get("bias", ""))
        qty = int(proposal.get("contracts", 0) or 0)
        underlying = proposal.get("ticker")
        exp = proposal.get("expiration")
        strike = proposal.get("strike")

        if "no trade" in structure or qty <= 0:
            return {"reject": True, "reason": "no tradable structure or zero size"}
        if strike is None or exp is None:
            return {"reject": True, "reason": "missing strike/expiration"}
        if "naked" in structure:
            return {"reject": True, "reason": "naked options not permitted"}

        strike = float(strike)
        w = max(0.01, self.spread_width_pct) * strike
        limit_price = proposal.get("limit_price")

        # Determine legs (action, option_type, strike).
        if "credit spread" in structure:
            if bias == "Bullish":   # put credit spread
                legs = [("sell_to_open", "put", strike),
                        ("buy_to_open", "put", round(strike - w, 2))]
            else:                   # call credit spread
                legs = [("sell_to_open", "call", strike),
                        ("buy_to_open", "call", round(strike + w, 2))]
            order_type = "credit"
        elif "spread" in structure:
            if bias == "Bullish":
                legs = [("buy_to_open", "call", strike),
                        ("sell_to_open", "call", round(strike + w, 2))]
            else:
                legs = [("buy_to_open", "put", strike),
                        ("sell_to_open", "put", round(strike - w, 2))]
            order_type = "debit"
        else:
            opt = "call" if bias == "Bullish" else "put"
            legs = [("buy_to_open", opt, strike)]
            order_type = "limit"

        params: dict = {"class": "multileg" if len(legs) > 1 else "option",
                        "symbol": underlying, "duration": self.duration, "type": order_type}
        if len(legs) == 1:
            action, opt_type, k = legs[0]
            params["option_symbol"] = occ_symbol(underlying, exp, opt_type, k)
            params["side"] = action
            params["quantity"] = qty
        else:
            for i, (action, opt_type, k) in enumerate(legs):
                params[f"option_symbol[{i}]"] = occ_symbol(underlying, exp, opt_type, k)
                params[f"side[{i}]"] = action
                params[f"quantity[{i}]"] = qty

        if limit_price is not None:
            params["price"] = limit_price
        else:
            params["_note"] = ("Set 'limit_price' on the proposal (net debit/credit "
                               "or single-leg limit) before placing a live order.")
        return {"reject": False, **params}

    # --- Routing ----------------------------------------------------------
    def preview(self, proposal: dict) -> dict:
        """Tradier preview (preview=true) — cost/margin/warnings, places nothing."""
        params = self.build_order_params(proposal)
        if params.get("reject"):
            return {"status": "REJECTED", "reason": params["reason"]}
        result = self._route(params, preview=True)
        return {"status": "PREVIEW", "order_params": _clean(params), "result": result}

    def submit(self, proposal: dict) -> dict:
        params = self.build_order_params(proposal)
        if params.get("reject"):
            return {"status": "REJECTED", "broker": self.name, "submitted": False,
                    "reason": params["reason"]}

        if not self.armed:
            return {"status": "STAGED", "broker": self.name, "submitted": False,
                    "order_params": _clean(params),
                    "note": "Unarmed: order built but NOT sent. Construct with "
                            "armed=True (token+account) to place. Preview first."}

        result = self._route(params, preview=False)
        return {"status": "SUBMITTED", "broker": self.name, "submitted": True,
                "order_params": _clean(params), "result": result}

    def _route(self, params: dict, preview: bool) -> dict:
        payload = {k: v for k, v in params.items() if not k.startswith("_") and k != "reject"}
        payload["preview"] = "true" if preview else "false"
        if self.sender is not None:
            return self.sender(payload, preview)
        if not self.token or not self.account_id:
            raise ValueError("TradierBroker needs token + account_id (or an injected sender) to route.")
        resp = requests.post(
            f"{self.base_url}/accounts/{self.account_id}/orders",
            data=payload,
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"},
            timeout=self.timeout,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Tradier order error {resp.status_code}: {resp.text[:300]}")
        return resp.json()


def occ_symbol(underlying: str, expiration: str, opt_type: str, strike: float) -> str:
    """Build an OCC option symbol, e.g. AAPL 2026-08-17 C 200 -> AAPL260817C00200000."""
    root = str(underlying).upper()
    yymmdd = "".join(str(expiration)[:10].split("-"))[2:]   # 2026-08-17 -> 260817
    cp = "C" if str(opt_type).lower().startswith("c") else "P"
    strike_int = int(round(float(strike) * 1000))
    return f"{root}{yymmdd}{cp}{strike_int:08d}"


def _clean(params: dict) -> dict:
    return {k: v for k, v in params.items() if k != "reject"}
