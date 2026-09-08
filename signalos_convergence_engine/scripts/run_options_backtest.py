"""Options P&L backtest + strategy A/B.

Runs the model-based option repricing backtest on a screened signal file and
prints the head-to-head: does the fundamental layer actually beat flow-only?

Example
-------
    python scripts/run_screen.py --demo
    python scripts/run_options_backtest.py --signals outputs/screen_signals.csv
"""
from pathlib import Path
import argparse
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.backtest.options_pnl import (
    backtest_option_pnl, compare_strategies, BacktestConfig,
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--signals", default=str(ROOT / "outputs" / "screen_signals.csv"))
    p.add_argument("--stock-daily", default=str(ROOT / "data" / "demo" / "stock_daily.csv"))
    p.add_argument("--horizon-days", type=int, default=20)
    p.add_argument("--target-pct", type=float, default=1.00)
    p.add_argument("--stop-pct", type=float, default=0.50)
    p.add_argument("--iv-shock", type=float, default=0.0,
                   help="Additive IV change over the hold (e.g. -0.10 for a vol crush)")
    args = p.parse_args()

    signals = pd.read_csv(args.signals)
    stocks = pd.read_csv(args.stock_daily)
    cfg = BacktestConfig(horizon_days=args.horizon_days, target_pct=args.target_pct,
                         stop_pct=args.stop_pct, iv_shock=args.iv_shock)

    tradable = signals[signals["decision"].isin(["A+ setup", "Tradable"])].copy()
    trades, summary = backtest_option_pnl(tradable, stocks, cfg)

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    trades.to_csv(out_dir / "options_backtest_trades.csv", index=False)
    summary.to_csv(out_dir / "options_backtest_summary.csv", index=False)

    print("=== Tradable book — options P&L summary ===")
    print(summary.to_string(index=False))

    print("\n=== Strategy A/B (marginal value of each layer) ===")
    comp = compare_strategies(signals, stocks, cfg)
    comp.to_csv(out_dir / "options_backtest_comparison.csv", index=False)
    print(comp.to_string(index=False))
    print(f"\nWrote options backtest outputs to {out_dir}")


if __name__ == "__main__":
    main()
