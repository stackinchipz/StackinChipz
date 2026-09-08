"""Databento OPRA provider — real options tape, replacing engine placeholders.

Why this matters more than another price feed:

The Tradier chain snapshot cannot see *who initiated* a trade, so
`tradier_provider.py` hardcodes:

    ask_side_ratio          = 0.65 / 0.55 / 0.50   (a constant!)
    repeat_flow_score       = 0.50                 (a constant!)
    avg_contract_volume_20d = volume / 2           (a guess)

Those drive 25 points of the 100-point UOA score AND `infer_bias()` — the
Bullish/Bearish call itself. Databento's OPRA feed gives the actual consolidated
tape (all 17 US options exchanges), so we can compute them for real:

    ask_side_ratio  <- quote-rule classification of each print vs the prevailing
                       NBBO (the `tbbo` schema pairs every trade with the book
                       state just before it)
    repeat_flow     <- persistence of buy-side pressure across the session
    sweep_score     <- multi-venue bursts (same contract, many exchanges, tight
                       time window) = the classic urgency/conviction signature
    avg_contract_volume_20d <- true trailing baseline from ohlcv-1d

Network calls need `pip install databento` and a `DATABENTO_API_KEY`. The pure
computation functions below are network-free and unit-tested.

Cost note: OPRA is not free (pay-as-you-go, or a Standard plan ~$199/mo at time
of writing). Everything degrades gracefully — no key, no problem, the engine
falls back to the Tradier placeholders.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np
import pandas as pd

OPRA_DATASET = "OPRA.PILLAR"
# Databento parent symbology: "AAPL.OPT" resolves to every AAPL option contract.
PARENT_SUFFIX = ".OPT"


# ---------------------------------------------------------------------------
# Pure computation (no network) — this is the part that fixes the placeholders
# ---------------------------------------------------------------------------
def classify_trade_side(price: float, bid: float, ask: float) -> str:
    """Lee-Ready quote rule: was this print buyer- or seller-initiated?

    at/above ask -> 'ask' (buyer paid up)
    at/below bid -> 'bid' (seller hit the bid)
    otherwise    -> compare to the midpoint; exactly at mid is 'mid'
    """
    if not np.isfinite(price) or not np.isfinite(bid) or not np.isfinite(ask):
        return "mid"
    if ask <= 0 or bid <= 0 or ask < bid:
        return "mid"
    if price >= ask:
        return "ask"
    if price <= bid:
        return "bid"
    mid = (bid + ask) / 2.0
    if price > mid:
        return "ask"
    if price < mid:
        return "bid"
    return "mid"


def compute_flow_features(
    trades: pd.DataFrame,
    sweep_window_ms: int = 500,
    sweep_min_venues: int = 3,
) -> pd.DataFrame:
    """Aggregate an OPRA trade tape into per-contract flow features.

    Expected columns (as produced by databento `tbbo`.to_df()):
        symbol, ts_event, price, size, bid_px_00, ask_px_00
        publisher_id (optional, enables sweep detection)

    Returns one row per contract with:
        ask_side_ratio      premium-weighted share of buyer-initiated flow [0,1]
        repeat_flow_score   persistence of ask-side flow across the session [0,1]
        sweep_score         share of ask-side premium done in multi-venue bursts
        premium_traded, trade_count, tape_volume
    """
    empty = pd.DataFrame(columns=[
        "option_symbol", "ask_side_ratio", "repeat_flow_score", "sweep_score",
        "premium_traded", "trade_count", "tape_volume",
    ])
    if trades is None or trades.empty:
        return empty

    df = trades.copy()
    if "symbol" in df.columns and "option_symbol" not in df.columns:
        df = df.rename(columns={"symbol": "option_symbol"})
    for c in ["price", "size", "bid_px_00", "ask_px_00"]:
        if c not in df.columns:
            df[c] = np.nan
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["ts_event"] = pd.to_datetime(df.get("ts_event"), errors="coerce", utc=True)
    df = df.dropna(subset=["option_symbol", "price", "size"])
    if df.empty:
        return empty

    df["side"] = [
        classify_trade_side(p, b, a)
        for p, b, a in zip(df["price"], df["bid_px_00"], df["ask_px_00"])
    ]
    # Options premium: price is per share, 100 shares per contract.
    df["premium"] = df["price"] * df["size"] * 100.0

    rows = []
    for symbol, g in df.groupby("option_symbol", sort=False):
        ask_prem = float(g.loc[g["side"] == "ask", "premium"].sum())
        bid_prem = float(g.loc[g["side"] == "bid", "premium"].sum())
        directional = ask_prem + bid_prem
        ask_side_ratio = ask_prem / directional if directional > 0 else 0.5

        asks = g[g["side"] == "ask"]
        rows.append({
            "option_symbol": symbol,
            "ask_side_ratio": round(float(np.clip(ask_side_ratio, 0.0, 1.0)), 4),
            "repeat_flow_score": _repeat_flow(asks, g),
            "sweep_score": _sweep_score(asks, sweep_window_ms, sweep_min_venues),
            "premium_traded": round(float(g["premium"].sum()), 2),
            "trade_count": int(len(g)),
            "tape_volume": int(g["size"].sum()),
        })
    return pd.DataFrame(rows)


def _repeat_flow(asks: pd.DataFrame, all_trades: pd.DataFrame) -> float:
    """Persistence of buy-side flow: sustained accumulation beats one big print.

    Blends (a) how many distinct minutes saw ask-side prints, and (b) how many
    distinct ask-side prints there were. One-and-done flow scores low even if
    the notional is large.
    """
    if asks.empty:
        return 0.0
    ts = asks["ts_event"].dropna()
    if ts.empty:
        breadth = 0.0
    else:
        active_minutes = ts.dt.floor("min").nunique()
        breadth = min(1.0, active_minutes / 12.0)     # ~12 active minutes -> full
    depth = min(1.0, len(asks) / 25.0)                # ~25 prints -> full
    return round(float(0.6 * breadth + 0.4 * depth), 4)


def _sweep_score(asks: pd.DataFrame, window_ms: int, min_venues: int) -> float:
    """Share of ask-side premium executed in multi-venue bursts (sweeps)."""
    if asks.empty or "publisher_id" not in asks.columns:
        return 0.0
    g = asks.dropna(subset=["ts_event"]).sort_values("ts_event")
    if g.empty:
        return 0.0
    total = float(g["premium"].sum())
    if total <= 0:
        return 0.0
    # Bucket prints into fixed windows; a bucket touching >= min_venues distinct
    # exchanges is a sweep.
    buckets = g["ts_event"].dt.floor(f"{window_ms}ms")
    swept = 0.0
    for _, b in g.groupby(buckets):
        if b["publisher_id"].nunique() >= min_venues:
            swept += float(b["premium"].sum())
    return round(float(np.clip(swept / total, 0.0, 1.0)), 4)


def enrich_option_chain(
    chain: pd.DataFrame,
    flow: pd.DataFrame,
    volume_baseline: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Replace the chain's placeholder flow fields with real tape-derived values.

    Contracts with no tape activity keep their existing (placeholder) values, so
    partial coverage never blanks out the screen.
    """
    out = chain.copy()
    if flow is None or flow.empty or "option_symbol" not in out.columns:
        return out

    f = flow.set_index("option_symbol")
    for col in ["ask_side_ratio", "repeat_flow_score"]:
        if col in f.columns:
            mapped = out["option_symbol"].map(f[col])
            out[col] = mapped.where(mapped.notna(), out.get(col))
    if "sweep_score" in f.columns:
        out["sweep_score"] = out["option_symbol"].map(f["sweep_score"]).fillna(0.0)
    if "premium_traded" in f.columns:
        out["tape_premium_traded"] = out["option_symbol"].map(f["premium_traded"])

    if volume_baseline is not None and not volume_baseline.empty:
        vb = volume_baseline.set_index("option_symbol")["avg_contract_volume_20d"]
        mapped = out["option_symbol"].map(vb)
        out["avg_contract_volume_20d"] = mapped.where(
            mapped.notna(), out.get("avg_contract_volume_20d"))
    return out


# ---------------------------------------------------------------------------
# Network client (requires `pip install databento` + DATABENTO_API_KEY)
# ---------------------------------------------------------------------------
@dataclass
class DatabentoOptionsProvider:
    api_key: str | None = None
    dataset: str = OPRA_DATASET

    def _client(self):
        try:
            import databento as db
        except ImportError as e:
            raise ImportError(
                "Databento client not installed. Run: pip install databento"
            ) from e
        return db.Historical(self.api_key) if self.api_key else db.Historical()

    @staticmethod
    def parent_symbols(underlyings: Iterable[str]) -> list[str]:
        return [f"{str(u).upper()}{PARENT_SUFFIX}" for u in underlyings]

    def fetch_option_trades(self, underlyings: Iterable[str], start: str,
                            end: str | None = None) -> pd.DataFrame:
        """OPRA trades paired with the prevailing NBBO (`tbbo` schema)."""
        data = self._client().timeseries.get_range(
            dataset=self.dataset,
            symbols=self.parent_symbols(underlyings),
            stype_in="parent",
            schema="tbbo",
            start=start,
            **({"end": end} if end else {}),
        )
        return data.to_df()

    def fetch_contract_volume_baseline(self, underlyings: Iterable[str], start: str,
                                       end: str | None = None,
                                       window: int = 20) -> pd.DataFrame:
        """True trailing per-contract volume baseline from daily OPRA bars."""
        data = self._client().timeseries.get_range(
            dataset=self.dataset,
            symbols=self.parent_symbols(underlyings),
            stype_in="parent",
            schema="ohlcv-1d",
            start=start,
            **({"end": end} if end else {}),
        )
        df = data.to_df()
        if df.empty:
            return pd.DataFrame(columns=["option_symbol", "avg_contract_volume_20d"])
        df = df.rename(columns={"symbol": "option_symbol"})
        df["ts_event"] = pd.to_datetime(df["ts_event"], errors="coerce", utc=True)
        df = df.sort_values("ts_event")
        base = (df.groupby("option_symbol")["volume"]
                  .apply(lambda s: float(s.tail(window).mean()))
                  .reset_index(name="avg_contract_volume_20d"))
        base["avg_contract_volume_20d"] = base["avg_contract_volume_20d"].clip(lower=1)
        return base

    def fetch_definitions(self, underlyings: Iterable[str], date: str) -> pd.DataFrame:
        """Point-in-time contract definitions (strike, expiration, call/put)."""
        data = self._client().timeseries.get_range(
            dataset=self.dataset,
            symbols=self.parent_symbols(underlyings),
            stype_in="parent",
            schema="definition",
            start=date,
        )
        df = data.to_df()
        if df.empty:
            return df
        keep = [c for c in ["symbol", "raw_symbol", "underlying", "strike_price",
                            "expiration", "instrument_class"] if c in df.columns]
        return df[keep].rename(columns={"symbol": "option_symbol"})
