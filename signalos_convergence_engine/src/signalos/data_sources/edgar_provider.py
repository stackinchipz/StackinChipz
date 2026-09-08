"""SEC EDGAR companyfacts provider (free US fundamentals).

Maps tickers -> CIK via the public company_tickers.json, then pulls annual
(10-K, form=="10-K", fp=="FY") XBRL facts and normalizes them into the
fundamentals contract in `fundamentals.py`.

Network note: requires egress to `www.sec.gov` and `data.sec.gov`. SEC asks
for a descriptive User-Agent with contact info; pass one via `user_agent`.
Rate limit is ~10 requests/sec — we sleep conservatively between calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import time
import pandas as pd
import requests


SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"

# XBRL us-gaap concept candidates, in priority order, per logical field.
CONCEPT_MAP = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax",
    ],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "total_assets": ["Assets"],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "total_debt": ["LongTermDebtNoncurrent", "LongTermDebt", "DebtLongtermAndShorttermCombinedAmount"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
    "depreciation_amortization": [
        "DepreciationDepletionAndAmortization",
        "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization",
    ],
    "rd_expense": ["ResearchAndDevelopmentExpense"],
    "goodwill": ["Goodwill"],
    "shares_diluted": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
}


@dataclass
class EdgarProvider:
    user_agent: str | None = None
    timeout: int = 30
    pause: float = 0.2

    @property
    def headers(self) -> dict:
        ua = self.user_agent or "SignalOS research contact@example.com"
        return {"User-Agent": ua, "Accept": "application/json"}

    def _get(self, url: str) -> dict:
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code >= 400:
            raise RuntimeError(f"EDGAR error {resp.status_code} for {url}: {resp.text[:200]}")
        return resp.json()

    def ticker_to_cik(self) -> dict[str, int]:
        data = self._get(SEC_TICKERS_URL)
        return {row["ticker"].upper(): int(row["cik_str"]) for row in data.values()}

    def _annual_series(self, facts: dict, field: str,
                       filed: dict[int, str] | None = None) -> dict[int, float]:
        """Return {fiscal_year: value} for the best-available concept of a field.

        If `filed` is provided, it is populated with {fiscal_year: filing_date}
        (the point-in-time date the value became public).
        """
        us_gaap = facts.get("facts", {}).get("us-gaap", {})
        for concept in CONCEPT_MAP[field]:
            node = us_gaap.get(concept)
            if not node:
                continue
            out: dict[int, float] = {}
            for unit_rows in node.get("units", {}).values():
                for r in unit_rows:
                    if r.get("form") != "10-K" or r.get("fp") != "FY":
                        continue
                    fy = r.get("fy")
                    val = r.get("val")
                    if fy is None or val is None:
                        continue
                    # Prefer the latest-filed value for a given fiscal year.
                    out[int(fy)] = float(val)
                    if filed is not None and r.get("filed"):
                        filed[int(fy)] = r["filed"]
            if out:
                return out
        return {}

    def fetch_company(self, ticker: str, cik: int, years: int = 6) -> pd.DataFrame:
        facts = self._get(SEC_FACTS_URL.format(cik=cik))
        filed: dict[int, str] = {}
        series = {field: self._annual_series(facts, field, filed) for field in CONCEPT_MAP}

        all_years = sorted({y for s in series.values() for y in s})[-years:]
        rows = []
        for fy in all_years:
            capex = series["capex"].get(fy)
            rows.append({
                "ticker": ticker.upper(),
                "fiscal_year": fy,
                "period_end": f"{fy}-12-31",
                "filing_date": filed.get(fy),
                "revenue": series["revenue"].get(fy),
                "operating_income": series["operating_income"].get(fy),
                "net_income": series["net_income"].get(fy),
                "total_assets": series["total_assets"].get(fy),
                "total_equity": series["total_equity"].get(fy),
                "total_debt": series["total_debt"].get(fy),
                "cash": series["cash"].get(fy),
                # EDGAR reports capex as a positive cash-outflow magnitude already.
                "capex": abs(capex) if capex is not None else None,
                "depreciation_amortization": series["depreciation_amortization"].get(fy),
                "rd_expense": series["rd_expense"].get(fy),
                "goodwill": series["goodwill"].get(fy),
                "shares_diluted": series["shares_diluted"].get(fy),
            })
        return pd.DataFrame(rows)

    def fetch_fundamentals(self, tickers: Iterable[str], years: int = 6) -> pd.DataFrame:
        cik_map = self.ticker_to_cik()
        frames = []
        for t in tickers:
            cik = cik_map.get(t.upper())
            if cik is None:
                continue
            try:
                df = self.fetch_company(t, cik, years=years)
                if not df.empty:
                    frames.append(df)
            except Exception:
                # Skip names EDGAR can't resolve; the screen tolerates gaps.
                continue
            time.sleep(self.pause)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
