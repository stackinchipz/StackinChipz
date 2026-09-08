"""SignalOS agent execution layer (propose-only by default).

Reads the screen, sizes each candidate through the risk engine, and emits
guarded trade *proposals* with a plain-English thesis and invalidation. It never
sends live orders unless a real broker is explicitly injected AND execute=True;
the default path is a dry run that only logs.

This is the safe scaffold that later plugs into a Robinhood/Tradier MCP locally
(see docs/ROBINHOOD_AGENT_SETUP.md). The risk engine is the last gate before any
order would leave — guardrails live here in code, not in a model prompt.
"""
from signalos.agent.proposals import TradeProposal, build_proposals
from signalos.agent.broker import ExecutionBroker, DryRunBroker, MCPBrokerStub
from signalos.agent.robinhood_broker import RobinhoodMCPBroker
from signalos.agent.tradier_broker import TradierBroker, occ_symbol
from signalos.agent.runtime import run_agent

__all__ = [
    "TradeProposal", "build_proposals",
    "ExecutionBroker", "DryRunBroker", "MCPBrokerStub", "RobinhoodMCPBroker",
    "TradierBroker", "occ_symbol",
    "run_agent",
]
