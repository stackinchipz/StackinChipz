"""Capital-efficiency feature: Uniform-Accounting-lite + ROIIC + capex productivity.

This is the fundamental edge layer. It answers the user's thesis directly:
*are companies deploying capex in a way that actually increases revenue and
profitability, on a distortion-adjusted basis?*

Three lenses, computed from the normalized fundamentals contract:

1. Uniform ROA (UAFRS-lite) - a PUBLIC APPROXIMATION of Uniform Accounting that
   removes common GAAP distortions (capitalizes R&D, strips goodwill and excess
   cash) to estimate true economic return on operating assets.
2. ROIIC - return on incremental invested capital: do *new* dollars earn?
3. Capex productivity - capex/depreciation, incremental revenue per $ capex,
   incremental operating margin, reinvestment runway.

Output: one snapshot row per ticker with the metrics used downstream by the
scoring layer.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from signalos.config import ScannerConfig, DEFAULT_CONFIG


def _cagr(first: float, last: float, periods: int) -> float:
    if first is None or last is None or first <= 0 or last <= 0 or periods <= 0:
        return np.nan
    return (last / first) ** (1.0 / periods) - 1.0


def _invested_capital(row: pd.Series) -> float:
    equity = float(row.get("total_equity") or 0.0)
    debt = float(row.get("total_debt") or 0.0)
    cash = float(row.get("cash") or 0.0)
    return equity + debt - cash


def _nopat(row: pd.Series, tax: float) -> float:
    return float(row.get("operating_income") or 0.0) * (1.0 - tax)


def _uniform_roa(g: pd.DataFrame, config: ScannerConfig) -> float:
    """UAFRS-lite Uniform ROA for the latest year of a single-ticker frame `g`."""
    last = g.iloc[-1]
    tax = config.assumed_tax_rate

    # Capitalize R&D: build a rolling capitalized-R&D asset balance and add the
    # current-year R&D back to earnings net of straight-line amortization.
    n = config.rd_amortization_years
    rd_hist = g["rd_expense"].fillna(0.0).tolist()
    cap_rd_balance = sum(rd_hist[-n:])                      # ~unamortized capitalized R&D
    amort_rd = cap_rd_balance / n if n else 0.0
    rd_addback = float(last.get("rd_expense") or 0.0) - amort_rd

    uniform_earnings = _nopat(last, tax) + rd_addback * (1.0 - tax)

    assets = float(last.get("total_assets") or 0.0)
    goodwill = float(last.get("goodwill") or 0.0)
    revenue = float(last.get("revenue") or 0.0)
    cash = float(last.get("cash") or 0.0)
    excess_cash = max(0.0, cash - revenue * config.excess_cash_pct_of_revenue)

    uniform_assets = assets - goodwill - excess_cash + cap_rd_balance
    if uniform_assets <= 0:
        return np.nan
    return uniform_earnings / uniform_assets


def compute_capital_efficiency(
    fundamentals: pd.DataFrame,
    config: ScannerConfig = DEFAULT_CONFIG,
    asof_date=None,
) -> pd.DataFrame:
    """Return one metrics row per ticker (latest fiscal year).

    Pass `asof_date` to compute point-in-time (only filings public by that date),
    which is required for a look-ahead-free historical backtest.
    """
    if fundamentals is None or fundamentals.empty:
        return pd.DataFrame()

    df = fundamentals.copy()
    if asof_date is not None:
        from signalos.data_sources.fundamentals import as_of
        df = as_of(df, asof_date)
        if df.empty:
            return pd.DataFrame()
    df = df.sort_values(["ticker", "fiscal_year"])
    tax = config.assumed_tax_rate
    cap_lb = config.roiic_lookback_years

    snapshots = []
    for ticker, g in df.groupby("ticker", sort=False):
        g = g.reset_index(drop=True)
        if len(g) < 2:
            continue
        last = g.iloc[-1]
        prev = g.iloc[-2]
        years = len(g) - 1

        # --- Uniform ROA + trend (distortion gap vs GAAP) ---
        uniform_roa = _uniform_roa(g, config)
        gaap_roa = (float(last.get("net_income") or 0.0) /
                    float(last.get("total_assets") or np.nan))
        # Uniform ROA 3y ago for the trend.
        if len(g) >= 4:
            uniform_roa_prior = _uniform_roa(g.iloc[: len(g) - 3], config)
        else:
            uniform_roa_prior = np.nan
        uniform_roa_trend = (uniform_roa - uniform_roa_prior
                             if pd.notna(uniform_roa) and pd.notna(uniform_roa_prior) else np.nan)

        # --- ROIIC: incremental NOPAT / incremental invested capital ---
        lb = min(cap_lb, years)
        base = g.iloc[-(lb + 1)]
        d_nopat = _nopat(last, tax) - _nopat(base, tax)
        d_ic = _invested_capital(last) - _invested_capital(base)
        roiic = d_nopat / d_ic if abs(d_ic) > 1e-9 else np.nan

        # --- Capex productivity ---
        capex = float(last.get("capex") or 0.0)
        dep = float(last.get("depreciation_amortization") or 0.0)
        capex_to_dep = capex / dep if dep > 0 else np.nan
        capex_cagr = _cagr(float(g.iloc[-(lb + 1)].get("capex") or np.nan),
                           float(last.get("capex") or np.nan), lb)

        # Revenue created per prior-year dollar of capex (1y lag).
        d_rev = float(last.get("revenue") or 0.0) - float(prev.get("revenue") or 0.0)
        prev_capex = float(prev.get("capex") or 0.0)
        incr_rev_per_capex = d_rev / prev_capex if prev_capex > 0 else np.nan

        # Incremental operating margin: are margins expanding as revenue grows?
        d_oi = float(last.get("operating_income") or 0.0) - float(prev.get("operating_income") or 0.0)
        incr_op_margin = d_oi / d_rev if abs(d_rev) > 1e-9 else np.nan

        # Reinvestment rate: capex / NOPAT (how much of profit is plowed back).
        nopat_last = _nopat(last, tax)
        reinvestment_rate = capex / nopat_last if nopat_last > 0 else np.nan

        revenue_cagr = _cagr(float(g.iloc[0].get("revenue") or np.nan),
                             float(last.get("revenue") or np.nan), years)
        op_margin = (float(last.get("operating_income") or 0.0) /
                     float(last.get("revenue") or np.nan))
        op_margin_prev = (float(prev.get("operating_income") or 0.0) /
                          float(prev.get("revenue") or np.nan))
        op_margin_trend = (op_margin - op_margin_prev
                           if pd.notna(op_margin) and pd.notna(op_margin_prev) else np.nan)

        snapshots.append({
            "ticker": ticker,
            "fiscal_year": int(last.get("fiscal_year")),
            "uniform_roa": uniform_roa,
            "gaap_roa": gaap_roa,
            "accounting_distortion": (uniform_roa - gaap_roa
                                      if pd.notna(uniform_roa) and pd.notna(gaap_roa) else np.nan),
            "uniform_roa_trend": uniform_roa_trend,
            "roiic": roiic,
            "capex_to_depreciation": capex_to_dep,
            "capex_cagr": capex_cagr,
            "incr_rev_per_capex": incr_rev_per_capex,
            "incr_op_margin": incr_op_margin,
            "reinvestment_rate": reinvestment_rate,
            "revenue_cagr": revenue_cagr,
            "op_margin": op_margin,
            "op_margin_trend": op_margin_trend,
        })

    return pd.DataFrame(snapshots)
