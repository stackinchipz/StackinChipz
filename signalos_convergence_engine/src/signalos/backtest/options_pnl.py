"""Options P&L backtest: model-based repricing along the realized path.

The original `simulator.py` uses an underlying-return proxy. This upgrades to an
option-level P&L simulation that captures convexity, theta decay and IV — the
things that actually determine a long-premium book's results.

Approach (transparent, no scipy dependency):
- Entry: buy the signal's contract at the ask (mid + half the quoted spread).
- Each forward business day, reprice with Black-Scholes using the realized
  underlying close, decayed time-to-expiry, and an IV assumption (held at entry
  IV by default; `iv_shock` lets you stress a vol crush/expansion).
- Exit on the FIRST of: target hit, stop hit, expiration, or horizon — selling
  at the modeled bid (model mid - half spread).
- Spreads (debit structures) are approximated as a fraction of single-option
  risk via `spread_debit_frac`, which caps both cost and payoff.

This is a MODEL backtest, not a historical-chain replay. A true replay needs
stored option-chain snapshots (see BACKLOG: DATA + CAP-003). Assumptions are
explicit so results are honest about their limits.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
import numpy as np
import pandas as pd


# --- Black-Scholes (erf-based normal CDF, no scipy) ---------------------------
def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_price(S: float, K: float, T: float, sigma: float, opt_type: str, r: float = 0.04) -> float:
    """European option price. T in years, sigma annualized."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        intrinsic = max(0.0, S - K) if opt_type == "call" else max(0.0, K - S)
        return float(intrinsic)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if opt_type == "call":
        return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
    return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


@dataclass
class BacktestConfig:
    horizon_days: int = 20
    target_pct: float = 1.00      # +100% take-profit on premium
    stop_pct: float = 0.50        # -50% stop on premium
    iv_shock: float = 0.0         # additive IV change applied over the hold (e.g. -0.10)
    risk_free: float = 0.04
    spread_debit_frac: float = 0.40   # debit-spread cost as frac of single-leg risk
    min_entry_price: float = 0.10


def _forward_path(stock_daily: pd.DataFrame) -> dict:
    """Map (ticker) -> sorted DataFrame of date/close for fast path lookups."""
    s = stock_daily.copy()
    s["date"] = pd.to_datetime(s["date"])
    s = s.sort_values(["ticker", "date"])
    return {t: g.reset_index(drop=True) for t, g in s.groupby("ticker")}


def _simulate_one(sig: pd.Series, path: pd.DataFrame, cfg: BacktestConfig) -> dict | None:
    opt_type = str(sig.get("type", "")).lower()
    if opt_type not in {"call", "put"}:
        return None

    K = float(sig.get("strike") or 0.0)
    iv0 = float(sig.get("implied_volatility") or 0.0)
    dte = int(sig.get("days_to_expiration") or 0)
    spread_pct = float(sig.get("spread_pct") or 0.10)
    half_spread = min(0.5, max(0.0, spread_pct) / 2.0)
    is_spread = "spread" in str(sig.get("suggested_structure", "")).lower() or \
                "spread" in str(sig.get("screen_structure", "")).lower()

    sig_date = pd.to_datetime(sig.get("date"))
    fwd = path[path["date"] >= sig_date].reset_index(drop=True)
    if len(fwd) < 2 or K <= 0 or iv0 <= 0 or dte <= 0:
        return None

    S0 = float(fwd.iloc[0]["close"])
    entry_mid = bs_price(S0, K, dte / 365.0, iv0, opt_type, cfg.risk_free)
    if entry_mid < cfg.min_entry_price:
        return None
    entry_fill = entry_mid * (1.0 + half_spread)     # pay the ask

    n = min(cfg.horizon_days, len(fwd) - 1, dte)
    exit_pct, exit_reason, days_held = None, "horizon", n
    iv_step = cfg.iv_shock / max(n, 1)

    for t in range(1, n + 1):
        S = float(fwd.iloc[t]["close"])
        T = max((dte - t) / 365.0, 1e-6)
        sigma = max(0.01, iv0 + iv_step * t)
        model_mid = bs_price(S, K, T, sigma, opt_type, cfg.risk_free)
        exit_fill = model_mid * (1.0 - half_spread)  # sell the bid
        pnl = exit_fill / entry_fill - 1.0
        if is_spread:
            # Debit spread caps payoff and loss relative to the single leg.
            pnl = max(-1.0, min(pnl, 1.0 / cfg.spread_debit_frac - 1.0)) * cfg.spread_debit_frac
        if pnl >= cfg.target_pct:
            exit_pct, exit_reason, days_held = cfg.target_pct, "target", t
            break
        if pnl <= -cfg.stop_pct:
            exit_pct, exit_reason, days_held = -cfg.stop_pct, "stop", t
            break

    if exit_pct is None:
        S = float(fwd.iloc[n]["close"])
        T = max((dte - n) / 365.0, 1e-6)
        sigma = max(0.01, iv0 + cfg.iv_shock)
        model_mid = bs_price(S, K, T, sigma, opt_type, cfg.risk_free)
        exit_fill = model_mid * (1.0 - half_spread)
        exit_pct = exit_fill / entry_fill - 1.0
        if is_spread:
            exit_pct = max(-1.0, min(exit_pct, 1.0 / cfg.spread_debit_frac - 1.0)) * cfg.spread_debit_frac

    return {
        "ticker": sig.get("ticker"),
        "bias": sig.get("bias"),
        "type": opt_type,
        "decision": sig.get("decision"),
        "screen": sig.get("screen", ""),
        "capital_verdict": sig.get("capital_verdict", ""),
        "convergence_score": sig.get("convergence_score"),
        "entry_underlying": round(S0, 2),
        "entry_price": round(entry_fill, 2),
        "option_return": round(float(exit_pct), 4),
        "exit_reason": exit_reason,
        "days_held": days_held,
    }


def backtest_option_pnl(signals: pd.DataFrame, stock_daily: pd.DataFrame,
                        cfg: BacktestConfig | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg = cfg or BacktestConfig()
    paths = _forward_path(stock_daily)

    trades = []
    for _, sig in signals.iterrows():
        t = sig.get("ticker")
        if t not in paths:
            continue
        res = _simulate_one(sig, paths[t], cfg)
        if res:
            trades.append(res)

    trades_df = pd.DataFrame(trades)
    return trades_df, summarize(trades_df)


def summarize(trades: pd.DataFrame) -> pd.DataFrame:
    if trades is None or trades.empty:
        return pd.DataFrame([{"num_trades": 0}])
    r = trades["option_return"]
    wins = r[r > 0]
    losses = r[r <= 0]
    profit_factor = (wins.sum() / abs(losses.sum())) if losses.sum() != 0 else np.inf
    payoff = (wins.mean() / abs(losses.mean())) if len(losses) and losses.mean() != 0 else np.nan
    # Equal-weight equity curve for max drawdown.
    eq = (1 + r).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    return pd.DataFrame([{
        "num_trades": len(r),
        "win_rate": round(float((r > 0).mean()), 4),
        "avg_return": round(float(r.mean()), 4),
        "median_return": round(float(r.median()), 4),
        "expectancy": round(float(r.mean()), 4),
        "profit_factor": round(float(profit_factor), 3),
        "payoff_ratio": round(float(payoff), 3) if pd.notna(payoff) else None,
        "max_drawdown": round(float(dd), 4),
    }])


def compare_strategies(signals: pd.DataFrame, stock_daily: pd.DataFrame,
                       cfg: BacktestConfig | None = None) -> pd.DataFrame:
    """A/B the marginal value of each layer: does fundamental beat flow-only?"""
    cfg = cfg or BacktestConfig()

    def _sub(df):
        return df[df["decision"].isin(["A+ setup", "Tradable"])].copy()

    flow_only = _sub(signals)
    convergence = _sub(signals[signals.get("convergence_score", 0) >= 70])

    # Convergence + fundamental agreement.
    if "capital_verdict" in signals.columns:
        bull_ok = signals["bias"].eq("Bullish") & signals["capital_verdict"].isin(["Compounder", "Quality"])
        bear_ok = signals["bias"].eq("Bearish") & signals["capital_verdict"].eq("Capital Destroyer")
        fundamental = _sub(signals[bull_ok | bear_ok])
    else:
        fundamental = convergence.iloc[0:0]

    rows = []
    for name, sub in [("Flow-only", flow_only),
                      ("Convergence>=70", convergence),
                      ("Convergence+Fundamental", fundamental)]:
        _, summ = backtest_option_pnl(sub, stock_daily, cfg)
        s = summ.iloc[0].to_dict()
        s["strategy"] = name
        rows.append(s)
    cols = ["strategy", "num_trades", "win_rate", "avg_return", "median_return",
            "profit_factor", "payoff_ratio", "max_drawdown"]
    out = pd.DataFrame(rows)
    return out[[c for c in cols if c in out.columns]]
