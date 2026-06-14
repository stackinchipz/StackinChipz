"""Robinhood MCP broker (Model B scaffold) — defined-risk, two-barrier safe.

Robinhood's agentic-trading MCP (`https://agent.robinhood.com/mcp/trading`,
server name `robinhood-trading`) attaches to an *agent runtime* (Claude Code,
Claude Desktop, or the Claude Agent SDK), not to arbitrary Python. So this
broker does not call Robinhood directly: it builds a normalized, defined-risk
**order spec** from a proposal and hands it to an injected `mcp_invoker` — a
callable you wire locally that actually drives the RH MCP order tool (e.g. from
an Agent-SDK session that has the MCP configured).

Safety — two independent barriers before anything is sent:
  1. the broker must be constructed with `armed=True`, AND
  2. a real `mcp_invoker` must be provided.
Default construction stages the order and returns it WITHOUT sending. There is
no naked-options path: non-defined-risk structures are rejected.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from signalos.agent.broker import ExecutionBroker

ROBINHOOD_MCP_URL = "https://agent.robinhood.com/mcp/trading"
ROBINHOOD_SERVER_NAME = "robinhood-trading"


class RobinhoodMCPBroker(ExecutionBroker):
    name = "robinhood-mcp"

    def __init__(
        self,
        armed: bool = False,
        mcp_invoker: Callable[[dict], dict] | None = None,
        spread_width_pct: float = 0.05,
        mcp_url: str = ROBINHOOD_MCP_URL,
        server_name: str = ROBINHOOD_SERVER_NAME,
    ):
        self.armed = armed
        self.mcp_invoker = mcp_invoker
        self.spread_width_pct = spread_width_pct
        self.mcp_url = mcp_url
        self.server_name = server_name

    # --- Order construction (defined-risk only) ---------------------------
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
        if "debit spread" in structure or ("call" in structure and "spread" in structure and "credit" not in structure) \
                or ("put" in structure and "spread" in structure and "credit" not in structure):
            # Long debit spread in the direction of the bias.
            if bias == "Bullish":
                legs = [_leg("buy_to_open", "call", strike, exp),
                        _leg("sell_to_open", "call", round(strike + w, 2), exp)]
            else:
                legs = [_leg("buy_to_open", "put", strike, exp),
                        _leg("sell_to_open", "put", round(strike - w, 2), exp)]
        elif "credit spread" in structure:
            # Defined-risk credit: sell near, buy further OTM for protection.
            if bias == "Bullish":   # put credit spread
                legs = [_leg("sell_to_open", "put", strike, exp),
                        _leg("buy_to_open", "put", round(strike - w, 2), exp)]
            else:                   # call credit spread
                legs = [_leg("sell_to_open", "call", strike, exp),
                        _leg("buy_to_open", "call", round(strike + w, 2), exp)]
        else:
            # Single long option.
            opt = "call" if bias == "Bullish" else "put"
            legs = [_leg("buy_to_open", opt, strike, exp)]

        return {
            "reject": False,
            "underlying": ticker,
            "quantity": qty,
            "legs": legs,
            "order_class": "multileg" if len(legs) > 1 else "option",
            "order_type": "limit",
            "time_in_force": "day",
            "defined_risk": True,
            "max_loss": proposal.get("dollar_risk"),
            "source": {"screen": proposal.get("screen"), "thesis": proposal.get("thesis")},
        }

    # --- Routing ----------------------------------------------------------
    def submit(self, proposal: dict) -> dict:
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
                f"drives the '{self.server_name}' MCP order tool "
                f"({self.mcp_url}); see docs/EXECUTION_RUNBOOK.md."
            )

        result = self.mcp_invoker(spec)
        return {"status": "SUBMITTED", "broker": self.name, "submitted": True,
                "order_spec": spec, "result": result,
                "routed_at": datetime.now(timezone.utc).isoformat()}


def _leg(action: str, option_type: str, strike: float, expiration: str, ratio: int = 1) -> dict:
    return {"action": action, "option_type": option_type, "strike": strike,
            "expiration": expiration, "ratio": ratio}
