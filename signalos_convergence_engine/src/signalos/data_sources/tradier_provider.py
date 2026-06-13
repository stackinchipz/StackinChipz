from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable

import pandas as pd
import requests


LIVE_BASE_URL = "https://api.tradier.com/v1"
SANDBOX_BASE_URL = "https://sandbox.tradier.com/v1"


@dataclass
class TradierProvider:
    token: str
    sandbox: bool = False
    timeout: int = 30

    @property
    def base_url(self) -> str:
        return SANDBOX_BASE_URL if self.sandbox else LIVE_BASE_URL

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        response = requests.get(url, headers=self.headers, params=params or {}, timeout=self.timeout)
        if response.status_code >= 400:
            raise RuntimeError(f"Tradier API error {response.status_code}: {response.text[:500]}")
        return response.json()

    def get_history(self, symbol: str, start: str, end: str, interval: str = "daily") -> pd.DataFrame:
        payload = self._get(
            "/markets/history",
            {"symbol": symbol, "interval": interval, "start": start, "end": end},
        )

        raw = payload.get("history", {}).get("day", [])
        if isinstance(raw, dict):
            raw = [raw]

        rows = []
        for r in raw or []:
            rows.append({
                "date": r.get("date"),
                "ticker": symbol.upper(),
                "open": r.get("open"),
                "high": r.get("high"),
                "low": r.get("low"),
                "close": r.get("close"),
                "volume": r.get("volume"),
            })

        return pd.DataFrame(rows)

    def get_expirations(self, symbol: str) -> list[str]:
        payload = self._get(
            "/markets/options/expirations",
            {"symbol": symbol, "includeAllRoots": "false", "strikes": "false"},
        )
        dates = payload.get("expirations", {}).get("date", [])
        if isinstance(dates, str):
            return [dates]
        return list(dates or [])

    def get_option_chain(self, symbol: str, expiration: str) -> pd.DataFrame:
        payload = self._get(
            "/markets/options/chains",
            {"symbol": symbol, "expiration": expiration, "greeks": "true"},
        )

        raw = payload.get("options", {}).get("option", [])
        if isinstance(raw, dict):
            raw = [raw]

        rows = []
        signal_date = date.today()

        for r in raw or []:
            greeks = r.get("greeks") or {}
            bid = _num(r.get("bid"))
            ask = _num(r.get("ask"))
            last = _num(r.get("last"))
            mid = (bid + ask) / 2 if bid > 0 and ask > 0 else max(last, 0.01)
            expiration_date = r.get("expiration_date") or expiration
            dte = _days_to_expiration(expiration_date, signal_date)

            opt_type = str(r.get("option_type") or r.get("type") or "").lower()
            if opt_type in {"c", "call"}:
                opt_type = "call"
            elif opt_type in {"p", "put"}:
                opt_type = "put"
            else:
                continue

            volume = int(_num(r.get("volume")))
            open_interest = int(_num(r.get("open_interest")))

            # Chain-only feed limitation:
            # true 20d contract-volume baseline needs stored historical snapshots.
            # Until we accumulate history, use a conservative placeholder.
            avg_contract_volume_20d = max(5, int(max(volume, 1) / 2))

            # Chain snapshots do not reliably identify ask-side/bid-side prints.
            # This placeholder gets replaced by an intraday tape connector later.
            volume_to_oi = volume / open_interest if open_interest else 0
            ask_side_ratio = 0.65 if volume_to_oi >= 1 else 0.55 if volume > 500 else 0.50

            rows.append({
                "date": signal_date.isoformat(),
                "ticker": symbol.upper(),
                "option_symbol": r.get("symbol"),
                "expiration": expiration_date,
                "strike": _num(r.get("strike")),
                "type": opt_type,
                "bid": bid,
                "ask": ask,
                "mid": round(mid, 4),
                "last": last,
                "volume": volume,
                "open_interest": open_interest,
                "avg_contract_volume_20d": avg_contract_volume_20d,
                "implied_volatility": _num(greeks.get("mid_iv") or greeks.get("smv_vol") or r.get("implied_volatility")),
                "delta": _num(greeks.get("delta")),
                "gamma": _num(greeks.get("gamma")),
                "theta": _num(greeks.get("theta")),
                "vega": _num(greeks.get("vega")),
                "days_to_expiration": dte,
                "ask_side_ratio": ask_side_ratio,
                "repeat_flow_score": 0.50,
                "catalyst_score": 0.50,
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df[df["mid"] > 0]
            df = df[df["days_to_expiration"] > 0]
        return df

    def fetch_stock_daily(self, symbols: Iterable[str], lookback_days: int = 320) -> pd.DataFrame:
        end = date.today()
        start = end - timedelta(days=lookback_days)
        frames = []
        for symbol in symbols:
            df = self.get_history(symbol, start.isoformat(), end.isoformat())
            if not df.empty:
                frames.append(df)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def fetch_option_chains(
        self,
        symbols: Iterable[str],
        min_dte: int = 14,
        max_dte: int = 90,
        expirations_per_symbol: int = 3,
    ) -> pd.DataFrame:
        frames = []
        today = date.today()

        for symbol in symbols:
            expirations = self.get_expirations(symbol)
            selected = []
            for exp in expirations:
                dte = _days_to_expiration(exp, today)
                if min_dte <= dte <= max_dte:
                    selected.append(exp)
                if len(selected) >= expirations_per_symbol:
                    break

            for exp in selected:
                df = self.get_option_chain(symbol, exp)
                if not df.empty:
                    frames.append(df)

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _num(value) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def _days_to_expiration(expiration: str, today: date) -> int:
    try:
        exp_date = datetime.strptime(expiration[:10], "%Y-%m-%d").date()
        return (exp_date - today).days
    except Exception:
        return 0
