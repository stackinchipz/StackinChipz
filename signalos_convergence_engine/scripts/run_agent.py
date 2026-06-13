"""Run the propose-only SignalOS agent over a screened signal file.

The agent sizes each candidate through the risk engine and emits guarded trade
proposals with a thesis + invalidation. It does NOT place live orders.

Example
-------
    python scripts/run_screen.py --demo
    python scripts/run_agent.py --signals outputs/screen_signals.csv
"""
from pathlib import Path
import argparse
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.agent import run_agent, DryRunBroker


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--signals", default=str(ROOT / "outputs" / "screen_signals.csv"))
    p.add_argument("--top", type=int, default=15)
    args = p.parse_args()

    signals = pd.read_csv(args.signals)
    out = run_agent(
        signals,
        broker=DryRunBroker(),
        execute=False,                     # propose-only; never sends
        audit_path=ROOT / "outputs" / "agent_proposals.jsonl",
    )

    proposals = out["proposals"]
    book = out["book"]

    rows = []
    for r in proposals:
        if r["contracts"] <= 0:
            continue
        rows.append({
            "ticker": r["ticker"], "bias": r["bias"], "screen": r["screen"],
            "structure": r["structure"], "contracts": r["contracts"],
            "$risk": r["dollar_risk"], "PG": r["power_gauge_rating"],
            "verdict": r["capital_verdict"], "IV": r["iv_regime"],
            "status": r["routing"]["status"],
        })
    table = pd.DataFrame(rows).head(args.top)

    print("=== SignalOS agent — PROPOSE-ONLY (no live orders) ===\n")
    if not table.empty:
        print(table.to_string(index=False))
    else:
        print("No sized proposals (risk caps or no qualifying setups).")

    if book:
        print(f"\nBook: {book.get('positions',0)} positions, "
              f"${book.get('open_risk',0):,.0f} open risk "
              f"({book.get('heat_pct',0)*100:.2f}% heat) | "
              f"Net Δ {book.get('net_delta',0):,.0f}  V {book.get('net_vega',0):,.1f}")

    # Show one full proposal narrative as an example.
    sized = [r for r in proposals if r["contracts"] > 0]
    if sized:
        ex = sized[0]
        print(f"\n--- Example proposal: {ex['ticker']} ---")
        print(f"Thesis:       {ex['thesis']}")
        print(f"Invalidation: {ex['invalidation']}")
        print(f"Entry:        {ex['entry_note']}")

    print(f"\nAudit log: {ROOT / 'outputs' / 'agent_proposals.jsonl'}")


if __name__ == "__main__":
    main()
