"""Expert/sentiment signal inputs (estimate revisions, insider activity, short interest).

These feed the Chaikin Power Gauge "Experts" bucket and a squeeze screen. Like
the fundamentals layer, everything normalizes to one contract so the engine is
provider-agnostic:

    ticker,
    estimate_revision_net,   # net analyst revisions over ~90d, fraction in [-1, 1]
                             #   (share revised up minus share revised down)
    insider_net_ratio,       # net insider buying over ~90d, in [-1, 1]
                             #   (buy value - sell value) / (buy + sell)
    short_interest_pct,      # short interest as a fraction of float [0, 1]
    days_to_cover            # short interest / avg daily volume

Providers: demo (offline), edgar_insider (Form 4, best-effort), or a CSV you
assemble from your data vendor (FMP/Finnhub/Ortex/etc.).
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd


EXPERT_COLUMNS = [
    "ticker", "estimate_revision_net", "insider_net_ratio",
    "short_interest_pct", "days_to_cover",
]

_COMPOUNDERS = {"NVDA", "MP", "OXY", "PLTR", "IREN"}
_DESTROYERS = {"FCX", "BMY"}
_SQUEEZE = {"IREN", "LYFT", "CRTO", "COIN"}   # high short interest demo names
_DEMO_TICKERS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "AMZN", "GOOGL",
    "MP", "FCX", "OXY", "XOM", "BMY", "CRTO", "LYFT", "QXO",
    "ALB", "PLTR", "COIN", "IREN",
]


def empty_expert() -> pd.DataFrame:
    return pd.DataFrame(columns=EXPERT_COLUMNS)


def validate_expert(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in EXPERT_COLUMNS:
        if c not in out.columns:
            out[c] = np.nan
    for c in EXPERT_COLUMNS:
        if c != "ticker":
            out[c] = pd.to_numeric(out[c], errors="coerce")
    out["ticker"] = out["ticker"].astype(str).str.upper()
    return out[EXPERT_COLUMNS].reset_index(drop=True)


def make_demo_expert(seed: int = 23) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for t in _DEMO_TICKERS:
        if t in _COMPOUNDERS:
            rev = rng.uniform(0.15, 0.45)
            ins = rng.uniform(0.10, 0.60)
        elif t in _DESTROYERS:
            rev = rng.uniform(-0.40, -0.10)
            ins = rng.uniform(-0.50, -0.05)
        else:
            rev = rng.uniform(-0.15, 0.20)
            ins = rng.uniform(-0.20, 0.25)
        if t in _SQUEEZE:
            si = rng.uniform(0.15, 0.35)
            dtc = rng.uniform(5.0, 12.0)
        else:
            si = rng.uniform(0.01, 0.08)
            dtc = rng.uniform(0.5, 3.0)
        rows.append({"ticker": t, "estimate_revision_net": round(rev, 3),
                     "insider_net_ratio": round(ins, 3),
                     "short_interest_pct": round(si, 3), "days_to_cover": round(dtc, 2)})
    return validate_expert(pd.DataFrame(rows))


def write_demo_expert(base_path: str | Path) -> Path:
    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)
    out = base / "expert_inputs.csv"
    make_demo_expert().to_csv(out, index=False)
    return out


def load_expert_signals(
    provider: str = "demo",
    tickers: Iterable[str] | None = None,
    *,
    csv_path: str | Path | None = None,
    edgar_user_agent: str | None = None,
) -> pd.DataFrame:
    provider = provider.lower()
    if provider == "demo":
        return make_demo_expert()
    if provider == "csv":
        if not csv_path:
            raise ValueError("provider='csv' requires csv_path")
        return validate_expert(pd.read_csv(csv_path))
    if provider == "edgar_insider":
        from signalos.data_sources.edgar_insider import EdgarInsiderProvider
        prov = EdgarInsiderProvider(user_agent=edgar_user_agent)
        return validate_expert(prov.fetch_insider_signals(list(tickers or [])))
    raise ValueError(f"Unknown expert provider: {provider}")
