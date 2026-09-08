"""Tradier beta fundamentals provider (Morningstar-sourced).

Tradier exposes Morningstar-backed fundamentals under /v1/markets/fundamentals/*
(beta; brokerage market-data entitlement required). This wraps the financials
endpoint and normalizes the annual statements into the fundamentals contract.

Because the beta payload shape varies by symbol/entitlement, parsing is
defensive: anything it can't find is left as NaN and the screen tolerates the
gap. Use this when you want live financials + the earnings calendar on the same
Tradier token that already feeds your option chains.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Any
import pandas as pd
import requests


LIVE_BASE_URL = "https://api.tradier.com/v1"
SANDBOX_BASE_URL = "https://sandbox.tradier.com/v1"

# Morningstar dataId -> our field. These ids are stable across Morningstar
# standardized statements; we search the payload for them regardless of nesting.
DATA_ID_MAP = {
    "revenue": ["OperatingRevenue", "TotalRevenue", "Revenue"],
    "operating_income": ["OperatingIncome"],
    "net_income": ["NetIncome", "NetIncomeContinuousOperations"],
    "total_assets": ["TotalAssets"],
    "total_equity": ["TotalEquity", "StockholdersEquity"],
    "total_debt": ["TotalDebt", "LongTermDebt"],
    "cash": ["CashAndCashEquivalents", "CashCashEquivalentsAndShortTermInvestments"],
    "capex": ["CapitalExpenditure", "PurchaseOfPPE"],
    "depreciation_amortization": ["DepreciationAndAmortization", "DepreciationAmortizationDepletion"],
    "rd_expense": ["ResearchAndDevelopment"],
    "goodwill": ["Goodwill"],
    "shares_diluted": ["DilutedAverageShares", "WeightedAverageDilutedShares"],
}


@dataclass
class TradierFundamentals:
    token: str
    sandbox: bool = False
    timeout: int = 30

    @property
    def base_url(self) -> str:
        return SANDBOX_BASE_URL if self.sandbox else LIVE_BASE_URL

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def _get(self, path: str, params: dict) -> Any:
        resp = requests.get(f"{self.base_url}{path}", headers=self.headers,
                            params=params, timeout=self.timeout)
        if resp.status_code >= 400:
            raise RuntimeError(f"Tradier fundamentals error {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    @staticmethod
    def _harvest(node: Any, data_ids: list[str], found: dict[int, float]) -> None:
        """Recursively scan the Morningstar payload for {dataId, value, fiscalYear}."""
        if isinstance(node, dict):
            did = node.get("dataId") or node.get("data_id")
            if did in data_ids:
                fy = node.get("fiscalYear") or node.get("asOfDate", "")[:4]
                val = node.get("value")
                try:
                    if fy and val is not None:
                        found[int(str(fy)[:4])] = float(val)
                except (ValueError, TypeError):
                    pass
            for v in node.values():
                TradierFundamentals._harvest(v, data_ids, found)
        elif isinstance(node, list):
            for v in node:
                TradierFundamentals._harvest(v, data_ids, found)

    def fetch_company(self, ticker: str, years: int = 6) -> pd.DataFrame:
        payload = self._get("/markets/fundamentals/financials", {"symbols": ticker.upper()})
        series: dict[str, dict[int, float]] = {}
        for field, ids in DATA_ID_MAP.items():
            found: dict[int, float] = {}
            self._harvest(payload, ids, found)
            series[field] = found

        all_years = sorted({y for s in series.values() for y in s})[-years:]
        rows = []
        for fy in all_years:
            capex = series["capex"].get(fy)
            rows.append({
                "ticker": ticker.upper(),
                "fiscal_year": fy,
                "period_end": f"{fy}-12-31",
                "revenue": series["revenue"].get(fy),
                "operating_income": series["operating_income"].get(fy),
                "net_income": series["net_income"].get(fy),
                "total_assets": series["total_assets"].get(fy),
                "total_equity": series["total_equity"].get(fy),
                "total_debt": series["total_debt"].get(fy),
                "cash": series["cash"].get(fy),
                "capex": abs(capex) if capex is not None else None,
                "depreciation_amortization": series["depreciation_amortization"].get(fy),
                "rd_expense": series["rd_expense"].get(fy),
                "goodwill": series["goodwill"].get(fy),
                "shares_diluted": series["shares_diluted"].get(fy),
            })
        return pd.DataFrame(rows)

    def fetch_fundamentals(self, tickers: Iterable[str], years: int = 6) -> pd.DataFrame:
        frames = []
        for t in tickers:
            try:
                df = self.fetch_company(t, years=years)
                if not df.empty:
                    frames.append(df)
            except Exception:
                continue
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def fetch_earnings_calendar(self, tickers: Iterable[str]) -> pd.DataFrame:
        """Next earnings date per ticker (for the earnings/IV-crush gate)."""
        rows = []
        for t in tickers:
            try:
                payload = self._get("/markets/fundamentals/calendars", {"symbols": t.upper()})
                found: dict[int, float] = {}
                # Reuse the harvester to locate the next earnings date string.
                dates: list[str] = []
                self._collect_earnings_dates(payload, dates)
                next_date = sorted([d for d in dates if d >= pd.Timestamp.today().strftime("%Y-%m-%d")])
                rows.append({"ticker": t.upper(), "next_earnings": next_date[0] if next_date else None})
            except Exception:
                rows.append({"ticker": t.upper(), "next_earnings": None})
        return pd.DataFrame(rows)

    @staticmethod
    def _collect_earnings_dates(node: Any, out: list[str]) -> None:
        if isinstance(node, dict):
            if str(node.get("event_type", "")).lower().find("earnings") >= 0:
                d = node.get("begin_date_time") or node.get("date")
                if d:
                    out.append(str(d)[:10])
            for v in node.values():
                TradierFundamentals._collect_earnings_dates(v, out)
        elif isinstance(node, list):
            for v in node:
                TradierFundamentals._collect_earnings_dates(v, out)
