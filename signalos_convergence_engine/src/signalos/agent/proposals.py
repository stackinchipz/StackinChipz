"""Build guarded trade proposals (with thesis + invalidation) from sized signals."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG


@dataclass
class TradeProposal:
    ticker: str
    bias: str
    screen: str
    structure: str
    decision: str
    # sizing (from the risk engine)
    contracts: int
    risk_pct: float
    max_loss_per_contract: float
    dollar_risk: float
    binding_constraint: str | None
    # conviction context
    convergence_score: float
    power_gauge_rating: str
    capital_verdict: str
    iv_regime: str
    # narrative
    thesis: str
    invalidation: str
    entry_note: str
    status: str = "PROPOSED"          # never auto-executed
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


def _f(row, key, default=0.0):
    v = row.get(key, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _thesis(row: pd.Series) -> str:
    bias = row.get("bias", "")
    verdict = str(row.get("capital_verdict", "Unknown"))
    pg = str(row.get("power_gauge_rating", "Neutral"))
    iv = str(row.get("iv_regime", "Unknown"))
    uroa = row.get("uniform_roa")
    roiic = row.get("roiic")
    bits = []
    if verdict in {"Compounder", "Quality"} and bias == "Bullish":
        bits.append(f"{verdict}: capex is converting to returns")
        if pd.notna(uroa):
            bits.append(f"Uniform ROA {float(uroa)*100:.0f}%")
        if pd.notna(roiic):
            bits.append(f"ROIIC {float(roiic)*100:.0f}%")
    elif verdict == "Capital Destroyer" and bias == "Bearish":
        bits.append("Capital Destroyer: heavy capex, sub-cost-of-capital returns, margins compressing")
        if pd.notna(roiic):
            bits.append(f"ROIIC {float(roiic)*100:.0f}%")
    bits.append(f"Power Gauge {pg}")
    bits.append(f"UOA {_f(row,'uoa_score'):.0f} / money flow {_f(row,'money_flow_score'):.0f} confirm {bias.lower()}")
    bits.append(f"IV {iv}")
    return "; ".join(bits) + "."


def _invalidation(row: pd.Series, config: ScannerConfig) -> str:
    bias = row.get("bias", "")
    stop = "premium stop -50%"
    if bias == "Bullish":
        flow = "CMF(21) flips negative or close breaks below 20DMA"
    elif bias == "Bearish":
        flow = "CMF(21) flips positive or close reclaims 20DMA"
    else:
        flow = "directional signal unclear"
    earn = ""
    edte = row.get("earnings_dte")
    if pd.notna(edte) and 0 <= float(edte) <= config.earnings_block_dte:
        earn = f"; earnings in {int(edte)}d — avoid naked long premium (use defined-risk)"
    return f"Exit if {flow}; {stop}{earn}."


def build_proposals(sized: pd.DataFrame, config: ScannerConfig = DEFAULT_CONFIG) -> list[TradeProposal]:
    if sized is None or sized.empty:
        return []
    proposals = []
    for _, row in sized.iterrows():
        structure = str(row.get("screen_structure") or row.get("suggested_structure") or "No trade")
        proposals.append(TradeProposal(
            ticker=str(row.get("ticker")),
            bias=str(row.get("bias", "")),
            screen=str(row.get("screen", "")),
            structure=structure,
            decision=str(row.get("decision", "")),
            contracts=int(row.get("contracts", 0) or 0),
            risk_pct=round(_f(row, "risk_pct"), 4),
            max_loss_per_contract=round(_f(row, "max_loss_per_contract"), 2),
            dollar_risk=round(_f(row, "dollar_risk"), 2),
            binding_constraint=row.get("binding_constraint"),
            convergence_score=round(_f(row, "convergence_score"), 2),
            power_gauge_rating=str(row.get("power_gauge_rating", "Neutral")),
            capital_verdict=str(row.get("capital_verdict", "Unknown")),
            iv_regime=str(row.get("iv_regime", "Unknown")),
            thesis=_thesis(row),
            invalidation=_invalidation(row, config),
            entry_note=str(row.get("screen_entry_note", "")),
        ))
    return proposals
