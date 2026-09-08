"""Execution broker abstraction.

The agent routes proposals through an ExecutionBroker. The default is a
DryRunBroker that NEVER sends an order - it only records intent. A real broker
(Robinhood MCP, Tradier) is wired locally where the OAuth token lives; the stub
here refuses to submit and points at the setup doc, so nothing in this repo can
accidentally place a live trade.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class ExecutionBroker(ABC):
    name: str = "abstract"

    @abstractmethod
    def submit(self, proposal: dict) -> dict:
        """Submit a sized proposal. Return a routing result dict."""
        raise NotImplementedError


class DryRunBroker(ExecutionBroker):
    """Records intent without sending. The only broker safe to run anywhere."""
    name = "dry-run"

    def submit(self, proposal: dict) -> dict:
        return {
            "status": "DRY_RUN",
            "broker": self.name,
            "submitted": False,
            "would_buy": {
                "ticker": proposal.get("ticker"),
                "structure": proposal.get("structure"),
                "contracts": proposal.get("contracts"),
                "dollar_risk": proposal.get("dollar_risk"),
            },
            "routed_at": datetime.now(timezone.utc).isoformat(),
        }


class MCPBrokerStub(ExecutionBroker):
    """Placeholder for a real Robinhood/Tradier MCP broker.

    Intentionally not implemented in this repo: a live brokerage connection and
    its OAuth token must live on your local machine, not in a shared/ephemeral
    environment. Implement `submit` against the MCP locally.
    """
    name = "mcp-stub"

    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint

    def submit(self, proposal: dict) -> dict:
        raise NotImplementedError(
            "No live broker is wired in this repo by design. Connect the "
            "Robinhood/Tradier MCP locally and implement submit(); see "
            "docs/ROBINHOOD_AGENT_SETUP.md."
        )
