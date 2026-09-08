"""EDGAR Form 4 insider-activity provider (best-effort).

Pulls recent Form 4 filings per ticker from the SEC submissions API and parses
transaction codes (P = open-market purchase, S = sale) from the primary XML to
estimate a net insider-buying ratio over the recent window.

Network note: requires egress to `www.sec.gov` and `data.sec.gov`. This is a
best-effort parser (Form 4 XML varies); anything it can't resolve is left NaN
and the engine tolerates the gap. Only insider net ratio is derived here;
estimate revisions and short interest come from your own data vendor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import re
import time
import pandas as pd
import requests


SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"


@dataclass
class EdgarInsiderProvider:
    user_agent: str | None = None
    timeout: int = 30
    pause: float = 0.2
    max_filings: int = 40

    @property
    def headers(self) -> dict:
        ua = self.user_agent or "SignalOS research contact@example.com"
        return {"User-Agent": ua, "Accept": "application/json"}

    def _get(self, url: str):
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code >= 400:
            raise RuntimeError(f"EDGAR insider error {resp.status_code} for {url}")
        return resp

    def ticker_to_cik(self) -> dict[str, int]:
        data = self._get(SEC_TICKERS_URL).json()
        return {row["ticker"].upper(): int(row["cik_str"]) for row in data.values()}

    def _net_ratio_for_cik(self, cik: int) -> float:
        subs = self._get(SUBMISSIONS_URL.format(cik=cik)).json()
        recent = subs.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accns = recent.get("accessionNumber", [])
        docs = recent.get("primaryDocument", [])

        buy_val = sell_val = 0.0
        seen = 0
        for form, acc, doc in zip(forms, accns, docs):
            if form != "4" or not doc.endswith(".xml"):
                continue
            seen += 1
            if seen > self.max_filings:
                break
            url = ARCHIVE.format(cik=cik, acc_nodash=acc.replace("-", ""), doc=doc)
            try:
                xml = self._get(url).text
            except Exception:
                continue
            # Pair each transaction code with the nearest share/value figures.
            for m in re.finditer(r"<transactionAcquiredDisposedCode>.*?<value>([AD])</value>", xml, re.S):
                tail = xml[m.start(): m.start() + 1200]
                shares = _first_float(tail, r"<transactionShares>.*?<value>([\d.]+)</value>")
                price = _first_float(tail, r"<transactionPricePerShare>.*?<value>([\d.]+)</value>")
                notional = shares * price if shares and price else shares
                if m.group(1) == "A":
                    buy_val += notional
                else:
                    sell_val += notional
            time.sleep(self.pause)

        total = buy_val + sell_val
        if total <= 0:
            return float("nan")
        return (buy_val - sell_val) / total

    def fetch_insider_signals(self, tickers: Iterable[str]) -> pd.DataFrame:
        cik_map = self.ticker_to_cik()
        rows = []
        for t in tickers:
            cik = cik_map.get(t.upper())
            ratio = float("nan")
            if cik is not None:
                try:
                    ratio = self._net_ratio_for_cik(cik)
                except Exception:
                    ratio = float("nan")
            rows.append({"ticker": t.upper(), "insider_net_ratio": ratio,
                         "estimate_revision_net": float("nan"),
                         "short_interest_pct": float("nan"), "days_to_cover": float("nan")})
            time.sleep(self.pause)
        return pd.DataFrame(rows)


def _first_float(text: str, pattern: str) -> float:
    m = re.search(pattern, text, re.S)
    if not m:
        return 0.0
    try:
        return float(m.group(1))
    except (TypeError, ValueError):
        return 0.0
