"""Robinhood MCP broker (Model B scaffold) — defined-risk, two-barrier safe.

Robinhood's agentic-trading MCP (`https://agent.robinhood.com/mcp/trading`,
server name `robinhood-trading`) attaches to an *agent runtime* (Claude Code,
Claude Desktop, or the Claude Agent SDK), not to arbitrary Python. So this
broker does not call Robinhood directly: it builds a normalized order **spec**
from a proposal and hands it to an injected `mcp_invoker` — a callable you wire
locally that actually drives the RH MCP order tools.

IMPORTANT — beta reality (verified 2026-06): the Robinhood agentic MCP is
**equities-only**. Its trade tools are `review_equity_order`, `place_equity_order`,
`cancel_equity_order` — there is NO options order tool yet (options/crypto/futures
are "coming soon"). So:
  - asset_class="equity" (default): maps directional conviction to an equity
    order the RH MCP can actually place today.
  - asset_class="option": builds the defined-risk options spec for Tradier or a
    future RH options tool; it is NOT executable on RH's current beta.

Safety — two independent barriers before anything sends:
  1. constructed with `armed=True`, AND
  2. a real `mcp_invoker` provided.
Default construction stages and returns the order WITHOUT sending. Naked / no-
trade / zero-size structures are rejected even when armed. The RH safety pattern
(`review_equity_order` then `place_equity_order`) is surfaced in the spec.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from signalos.agent.broker import ExecutionBroker

ROBINHOOD_MCP_URL = "https://agent.robinhood.com/mcp/trading"
ROBINHOOD_SERVER_NAME = "robinhood-trading"
# Verified Robinhood MCP trade tool names (equities-only beta).
RH_REVIEW_TOOL = "review_equity_order"
RH_PLACE_TOOL = "place_equity_order"
RH_CANCEL_TOOL = "cancel_equity_order"


class RobinhoodMCPBroker(ExecutionBroker):
    name = "robinhood-mcp"

    def __init__(
        self,
        armed: bool = False,
        mcp_invoker: Callable[[dict], dict] | None = None,
        asset_class: str = "equity",          # RH beta is equities-only
        equity_notional: float = 2000.0,       # $ per equity position (RH has no defined-risk premium)
        allow_short: bool = False,             # RH agentic beta is long-equity
        spread_width_pct: float = 0.05,
        mcp_url: str = ROBINHOOD_MCP_URL,
        server_name: str = ROBINHOOD_SERVER_NAME,
    ):
        self.armed = armed
        self.mcp_invoker = mcp_invoker
        self.asset_class = asset_class
        self.equity_notional = equity_notional
        self.allow_short = allow_short
        self.spread_width_pct = spread_width_pct
        self.mcp_url = mcp_url
        self.server_name = server_name

    # --- Equity order (what RH can execute TODAY) -------------------------
    def build_equity_order_spec(self, proposal: dict) -> dict:
        structure = str(proposal.get("structure", "")).lower()
        bias = str(proposal.get("bias", ""))
        ticker = proposal.get("ticker")
        if "no trade" in structure or int(proposal.get("contracts", 0) or 0) <= 0:
            return {"reject": True, "reason": "no tradable structure or zero size"}
        if bias == "Bearish" and not self.allow_short:
            return {"reject": True,
                    "reason": "RH agentic beta is long-equity; route bearish/options "
                              "via Tradier or express as puts (not supported on RH yet)"}
        return {
            "reject": False,
            "asset_class": "equity",
            "symbol": ticker,
            "side": "buy" if bias == "Bullish" else "sell",
            "notional_usd": self.equity_notional,
            "order_type": "limit",
            "time_in_force": "day",
            "review_tool": RH_REVIEW_TOOL,
            "place_tool": RH_PLACE_TOOL,
            "note": "Call review_equity_order first, then place_equity_order.",
            "source": {"screen": proposal.get("screen"), "thesis": proposal.get("thesis"),
                       "capital_verdict": proposal.get("capital_verdict")},
        }

    # --- Options order (Tradier / future RH options tool) -----------------
    def build_order_spec(self, proposal: dict) -> dict:
        structure = str(proposal.get("structure", "")).lower()
        bias = str(proposal.get("bias", ""))
        qty = int(proposal.get("contracts", 0) or 0)
        ticker = proposal.get("ticker")
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

        legs: list[dict] = []
        if "credit spread" in structure:
            if bias == "Bullish":   # put credit spread
                legs = [_leg("sell_to_open", "put", strike, exp),
                        _leg("buy_to_open", "put", round(strike - w, 2), exp)]
            else:                   # call credit spread
                legs = [_leg("sell_to_open", "call", strike, exp),
                        _leg("buy_to_open", "call", round(strike + w, 2), exp)]
        elif "spread" in structure:
            if bias == "Bullish":
                legs = [_leg("buy_to_open", "call", strike, exp),
                        _leg("sell_to_open", "call", round(strike + w, 2), exp)]
            else:
                legs = [_leg("buy_to_open", "put", strike, exp),
                        _leg("sell_to_open", "put", round(strike - w, 2), exp)]
        else:
            opt = "call" if bias == "Bullish" else "put"
            legs = [_leg("buy_to_open", opt, strike, exp)]

        return {
            "reject": False,
            "asset_class": "option",
            "underlying": ticker,
            "quantity": qty,
            "legs": legs,
            "order_class": "multileg" if len(legs) > 1 else "option",
            "order_type": "limit",
            "time_in_force": "day",
            "defined_risk": True,
            "max_loss": proposal.get("dollar_risk"),
            "venue_note": "RH agentic beta is equities-only; execute via Tradier "
                          "or await RH options tools.",
            "source": {"screen": proposal.get("screen"), "thesis": proposal.get("thesis")},
        }

    # --- Routing ----------------------------------------------------------
    def submit(self, proposal: dict) -> dict:
        if self.asset_class == "equity":
            spec = self.build_equity_order_spec(proposal)
        else:
            spec = self.build_order_spec(proposal)

        if spec.get("reject"):
            return {"status": "REJECTED", "broker": self.name, "submitted": False,
                    "reason": spec["reason"]}

        if not self.armed:
            return {"status": "STAGED", "broker": self.name, "submitted": False,
                    "order_spec": spec,
                    "note": "Unarmed: order built but NOT sent. Construct with "
                            "armed=True and an mcp_invoker to place locally."}

        if self.mcp_invoker is None:
            raise NotImplementedError(
                "Armed but no mcp_invoker provided. Wire a local callable that "
                f"drives the '{self.server_name}' MCP order tools "
                f"({self.mcp_url}); see docs/EXECUTION_RUNBOOK.md."
            )

        result = self.mcp_invoker(spec)
        return {"status": "SUBMITTED", "broker": self.name, "submitted": True,
                "order_spec": spec, "result": result,
                "routed_at": datetime.now(timezone.utc).isoformat()}


def _leg(action: str, option_type: str, strike: float, expiration: str, ratio: int = 1) -> dict:
    return {"action": action, "option_type": option_type, "strike": strike,
            "expiration": expiration, "ratio": ratio}
