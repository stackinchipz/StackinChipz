"""Risk engine: position sizing, portfolio heat, book-level Greeks, kill-switch.

For an aggressive long-premium options book the alpha engine finds *what* to
trade; this decides *how much* and whether the book can take it at all. Nothing
here is the model's judgment - these are deterministic guardrails, which is the
only acceptable thing standing between an agent and the account.

Definitions:
    max-loss per contract:
        long option        -> mid * 100 (premium can go to zero)
        debit spread       -> debit * 100 (defined risk)
    risk per trade  = account_size * risk_pct
    contracts       = floor(risk_budget / max_loss_per_contract)
    portfolio heat  = sum(open risk) / account_size
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import numpy as np
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG


@dataclass
class RiskState:
    """Live book state the engine sizes against."""
    account_size: float = 100_000.0
    open_risk: float = 0.0                 # dollars currently at risk
    day_pnl_pct: float = 0.0               # realized+unrealized P&L on the day (fraction)
    sector_open_risk: dict = field(default_factory=dict)
    num_positions: int = 0


def _max_loss_per_contract(row: pd.Series) -> float:
    """Defined-risk max loss per contract in dollars."""
    structure = str(row.get("suggested_structure", "")).lower()
    mid = float(row.get("mid", 0.0) or 0.0)
    if "spread" in structure:
        # Debit spread: approximate debit as ~40% of the long-leg mid.
        debit = max(0.05, mid * 0.40)
        return debit * 100.0
    # Long single option: full premium at risk.
    return max(0.05, mid) * 100.0


def size_position(row: pd.Series, state: RiskState, config: ScannerConfig = DEFAULT_CONFIG) -> dict:
    """Return sizing + the binding constraint (if any) for one candidate."""
    decision = str(row.get("decision", ""))
    risk_pct = config.aplus_risk_per_trade_pct if decision == "A+ setup" else config.max_risk_per_trade_pct
    risk_budget = state.account_size * risk_pct
    max_loss = _max_loss_per_contract(row)
    contracts = int(math.floor(risk_budget / max_loss)) if max_loss > 0 else 0

    constraint = None
    # Headroom against the portfolio-heat cap.
    heat_cap = state.account_size * config.max_portfolio_heat_pct
    heat_headroom = heat_cap - state.open_risk
    if contracts * max_loss > heat_headroom:
        contracts = max(0, int(math.floor(heat_headroom / max_loss)))
        constraint = "portfolio-heat cap"

    # Per-sector cap.
    sector = row.get("sector", "Unknown")
    sector_cap = state.account_size * config.max_sector_heat_pct
    sector_used = state.sector_open_risk.get(sector, 0.0)
    sector_headroom = sector_cap - sector_used
    if contracts * max_loss > sector_headroom:
        contracts = max(0, int(math.floor(sector_headroom / max_loss)))
        constraint = f"sector cap ({sector})"

    # Hard book limits.
    if state.num_positions >= config.max_positions:
        contracts, constraint = 0, "max positions reached"
    if state.day_pnl_pct <= -config.daily_drawdown_kill_pct:
        contracts, constraint = 0, "daily drawdown kill-switch"

    dollar_risk = contracts * max_loss
    return {
        "risk_pct": risk_pct,
        "risk_budget": round(risk_budget, 2),
        "max_loss_per_contract": round(max_loss, 2),
        "contracts": contracts,
        "dollar_risk": round(dollar_risk, 2),
        "binding_constraint": constraint,
    }


def aggregate_book_greeks(positions: pd.DataFrame) -> dict:
    """Net Δ/Γ/Θ/V across a book of sized positions.

    `positions` needs: contracts, bias, type, delta, gamma, theta, vega.
    Deltas are signed by option type; short legs are not modeled here (the
    engine only proposes long/debit structures).
    """
    if positions is None or positions.empty:
        return {"net_delta": 0.0, "net_gamma": 0.0, "net_theta": 0.0, "net_vega": 0.0}
    p = positions.copy()
    qty = pd.to_numeric(p.get("contracts"), errors="coerce").fillna(0) * 100.0
    sign = np.where(p["type"].astype(str).str.lower() == "put", -1.0, 1.0)
    delta = pd.to_numeric(p.get("delta"), errors="coerce").fillna(0).abs() * sign
    return {
        "net_delta": round(float((delta * qty).sum()), 1),
        "net_gamma": round(float((pd.to_numeric(p.get("gamma"), errors="coerce").fillna(0) * qty).sum()), 2),
        "net_theta": round(float((pd.to_numeric(p.get("theta"), errors="coerce").fillna(0) * qty).sum()), 2),
        "net_vega": round(float((pd.to_numeric(p.get("vega"), errors="coerce").fillna(0) * qty).sum()), 2),
    }


def portfolio_heat(positions: pd.DataFrame, account_size: float) -> dict:
    if positions is None or positions.empty or account_size <= 0:
        return {"open_risk": 0.0, "heat_pct": 0.0}
    open_risk = float(pd.to_numeric(positions.get("dollar_risk"), errors="coerce").fillna(0).sum())
    return {"open_risk": round(open_risk, 2), "heat_pct": round(open_risk / account_size, 4)}


def apply_risk_engine(signals: pd.DataFrame, config: ScannerConfig = DEFAULT_CONFIG,
                      state: RiskState | None = None) -> pd.DataFrame:
    """Walk tradable signals top-down, sizing each against live book heat."""
    if signals is None or signals.empty:
        return signals
    state = state or RiskState(account_size=config.account_size)

    tradable = signals[signals["decision"].isin(["A+ setup", "Tradable"])].copy()
    rows = []
    for _, row in tradable.iterrows():
        sizing = size_position(row, state, config)
        merged = {**row.to_dict(), **sizing}
        rows.append(merged)
        # Update live book state so the next candidate sees reduced headroom.
        if sizing["contracts"] > 0:
            state.open_risk += sizing["dollar_risk"]
            state.num_positions += 1
            sec = row.get("sector", "Unknown")
            state.sector_open_risk[sec] = state.sector_open_risk.get(sec, 0.0) + sizing["dollar_risk"]

    sized = pd.DataFrame(rows)
    if not sized.empty:
        book = portfolio_heat(sized, state.account_size)
        greeks = aggregate_book_greeks(sized)
        sized.attrs["book"] = {**book, **greeks, "positions": int((sized["contracts"] > 0).sum())}
    return sized
