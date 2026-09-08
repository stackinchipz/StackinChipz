"""Unified fundamentals layer.

The capital-efficiency screen consumes a single normalized fundamentals
schema regardless of where the numbers come from. Providers (SEC EDGAR,
Tradier/Morningstar, or a demo generator) all emit this contract:

Required columns (one row per ticker per fiscal year):

    ticker, fiscal_year, period_end,
    revenue, operating_income, net_income,
    total_assets, total_equity, total_debt, cash,
    capex, depreciation_amortization, rd_expense,
    goodwill, shares_diluted

`capex` is stored as a POSITIVE number (cash spent on PP&E).

Use `load_fundamentals(...)` as the single entry point.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd


FUNDAMENTAL_COLUMNS = [
    "ticker", "fiscal_year", "period_end", "filing_date",
    "revenue", "operating_income", "net_income",
    "total_assets", "total_equity", "total_debt", "cash",
    "capex", "depreciation_amortization", "rd_expense",
    "goodwill", "shares_diluted",
]


def empty_fundamentals() -> pd.DataFrame:
    return pd.DataFrame(columns=FUNDAMENTAL_COLUMNS)


def validate_fundamentals(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce to the contract; fill missing optional columns with NaN/0."""
    out = df.copy()
    for col in FUNDAMENTAL_COLUMNS:
        if col not in out.columns:
            out[col] = np.nan
    numeric = [c for c in FUNDAMENTAL_COLUMNS if c not in {"ticker", "period_end", "filing_date"}]
    for c in numeric:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out["ticker"] = out["ticker"].astype(str).str.upper()
    out = out.sort_values(["ticker", "fiscal_year"]).reset_index(drop=True)
    return out[FUNDAMENTAL_COLUMNS]


def as_of(fundamentals: pd.DataFrame, asof_date) -> pd.DataFrame:
    """Point-in-time filter: keep only rows whose filing_date <= asof_date.

    Prevents look-ahead in historical screens/backtests — a fiscal year's data
    is only usable once it was actually filed. Rows with an unknown filing_date
    (NaT) are kept (conservative fallback for providers without filing dates).
    """
    if fundamentals is None or fundamentals.empty or asof_date is None:
        return fundamentals
    df = fundamentals.copy()
    asof = pd.to_datetime(asof_date)
    fd = pd.to_datetime(df.get("filing_date"), errors="coerce")
    return df[fd.isna() | (fd <= asof)].reset_index(drop=True)


def load_fundamentals(
    provider: str = "demo",
    tickers: Iterable[str] | None = None,
    *,
    csv_path: str | Path | None = None,
    tradier_token: str | None = None,
    edgar_user_agent: str | None = None,
    years: int = 6,
) -> pd.DataFrame:
    """Single entry point for fundamentals.

    provider:
        "demo"     -> deterministic synthetic data (offline, for testing)
        "csv"      -> read a pre-normalized CSV (csv_path)
        "edgar"    -> SEC EDGAR companyfacts (free; needs network egress to sec.gov)
        "tradier"  -> Tradier beta fundamentals (Morningstar-sourced; needs token)
    """
    provider = provider.lower()

    if provider == "demo":
        return make_demo_fundamentals(years=years)

    if provider == "csv":
        if not csv_path:
            raise ValueError("provider='csv' requires csv_path")
        return validate_fundamentals(pd.read_csv(csv_path))

    if provider == "edgar":
        from signalos.data_sources.edgar_provider import EdgarProvider
        prov = EdgarProvider(user_agent=edgar_user_agent)
        return validate_fundamentals(prov.fetch_fundamentals(list(tickers or []), years=years))

    if provider == "tradier":
        from signalos.data_sources.tradier_fundamentals import TradierFundamentals
        if not tradier_token:
            raise ValueError("provider='tradier' requires tradier_token")
        prov = TradierFundamentals(token=tradier_token)
        return validate_fundamentals(prov.fetch_fundamentals(list(tickers or []), years=years))

    raise ValueError(f"Unknown fundamentals provider: {provider}")


# ---------------------------------------------------------------------------
# Demo fundamentals generator
# ---------------------------------------------------------------------------
# Tickers tagged "compounder" mirror the bullish options-flow demo names, and
# "destroyer" tickers mirror the bearish demo names, so the merged screen tells
# a coherent story end-to-end (flow + fundamentals agree).
_COMPOUNDERS = {"NVDA", "MP", "OXY", "PLTR", "IREN"}
_DESTROYERS = {"FCX", "BMY"}
_DEMO_TICKERS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "AMZN", "GOOGL",
    "MP", "FCX", "OXY", "XOM", "BMY", "CRTO", "LYFT", "QXO",
    "ALB", "PLTR", "COIN", "IREN",
]


def make_demo_fundamentals(years: int = 6, seed: int = 17) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    current_year = pd.Timestamp.today().year

    for ticker in _DEMO_TICKERS:
        rev = rng.uniform(2_000, 60_000) * 1e6     # base revenue
        op_margin = rng.uniform(0.08, 0.30)
        assets = rev * rng.uniform(1.0, 2.2)
        equity_ratio = rng.uniform(0.35, 0.7)
        capex_intensity = rng.uniform(0.04, 0.10)   # capex / revenue
        rd_intensity = rng.uniform(0.0, 0.16) if ticker not in {"OXY", "XOM", "FCX", "MP", "ALB"} else rng.uniform(0.0, 0.02)

        if ticker in _COMPOUNDERS:
            rev_growth = rng.uniform(0.18, 0.40)     # fast, accelerating top line
            margin_drift = rng.uniform(0.004, 0.012) # margins EXPANDING while investing
            capex_growth = rng.uniform(0.20, 0.45)   # heavy growth capex
            capex_intensity = rng.uniform(0.08, 0.16)
        elif ticker in _DESTROYERS:
            rev_growth = rng.uniform(-0.04, 0.05)    # flat/declining top line
            margin_drift = rng.uniform(-0.015, -0.004)  # margins COMPRESSING
            capex_growth = rng.uniform(0.10, 0.30)   # still pouring in capex...
            capex_intensity = rng.uniform(0.09, 0.18)  # ...that isn't paying off
        else:
            rev_growth = rng.uniform(0.02, 0.12)
            margin_drift = rng.uniform(-0.004, 0.006)
            capex_growth = rng.uniform(0.0, 0.12)

        for i in range(years):
            fy = current_year - (years - 1 - i)
            growth_factor = (1 + rev_growth) ** i
            revenue = rev * growth_factor
            margin = max(0.02, op_margin + margin_drift * i)
            operating_income = revenue * margin
            net_income = operating_income * (1 - 0.21) * rng.uniform(0.85, 1.05)
            total_assets = assets * growth_factor * rng.uniform(0.98, 1.04)
            total_equity = total_assets * equity_ratio
            total_debt = total_assets * rng.uniform(0.10, 0.35)
            cash = revenue * rng.uniform(0.05, 0.20)
            capex = revenue * capex_intensity * ((1 + capex_growth) ** i) / growth_factor
            dep = capex * rng.uniform(0.45, 0.85)   # capex > depreciation = growth capex
            rd = revenue * rd_intensity
            goodwill = total_assets * (rng.uniform(0.15, 0.35) if ticker in _DESTROYERS else rng.uniform(0.0, 0.12))
            shares = rng.uniform(200, 3000) * 1e6

            rows.append({
                "ticker": ticker,
                "fiscal_year": fy,
                "period_end": f"{fy}-12-31",
                # 10-K typically filed ~2 months after fiscal year-end; this is
                # the date the data actually became public (point-in-time).
                "filing_date": f"{fy + 1}-03-01",
                "revenue": round(revenue, 0),
                "operating_income": round(operating_income, 0),
                "net_income": round(net_income, 0),
                "total_assets": round(total_assets, 0),
                "total_equity": round(total_equity, 0),
                "total_debt": round(total_debt, 0),
                "cash": round(cash, 0),
                "capex": round(capex, 0),
                "depreciation_amortization": round(dep, 0),
                "rd_expense": round(rd, 0),
                "goodwill": round(goodwill, 0),
                "shares_diluted": round(shares, 0),
            })

    return validate_fundamentals(pd.DataFrame(rows))


def write_demo_fundamentals(base_path: str | Path) -> Path:
    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)
    df = make_demo_fundamentals()
    out = base / "fundamentals.csv"
    df.to_csv(out, index=False)
    return out
