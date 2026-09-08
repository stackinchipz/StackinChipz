"""Agent runtime: size -> propose -> (dry-run) route -> audit log.

Default behavior is propose-only. Live execution requires BOTH an explicit
non-dry-run broker AND execute=True - two independent barriers - so the safe
path can never accidentally send an order.
"""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG
from signalos.pipeline_screen import size_screen
from signalos.agent.proposals import build_proposals
from signalos.agent.broker import ExecutionBroker, DryRunBroker


def run_agent(
    signals: pd.DataFrame,
    config: ScannerConfig = DEFAULT_CONFIG,
    broker: ExecutionBroker | None = None,
    execute: bool = False,
    audit_path: str | Path | None = None,
) -> dict:
    """Run the propose-only agent over a screened signal table.

    Returns {"proposals": [...], "book": {...}}. Writes a JSONL audit log if
    `audit_path` is given.
    """
    broker = broker or DryRunBroker()
    sized = size_screen(signals, config)
    book = dict(sized.attrs.get("book", {})) if sized is not None else {}
    proposals = build_proposals(sized, config)

    records = []
    for p in proposals:
        rec = p.to_dict()
        if p.contracts <= 0:
            rec["routing"] = {"status": "SKIPPED",
                              "reason": p.binding_constraint or "zero size"}
        elif execute:
            # Two barriers cleared: an explicit broker + execute=True.
            rec["routing"] = broker.submit(rec)
        else:
            rec["routing"] = {"status": "PROPOSED", "submitted": False}
        records.append(rec)

    if audit_path:
        path = Path(audit_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as fh:
            for rec in records:
                fh.write(json.dumps(rec, default=str) + "\n")

    return {"proposals": records, "book": book}
