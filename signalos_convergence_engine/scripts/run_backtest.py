from pathlib import Path
import argparse
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.backtest.simulator import backtest_underlying_returns


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--signals", required=True)
    parser.add_argument("--stock-daily", default=str(ROOT / "data" / "demo" / "stock_daily.csv"))
    parser.add_argument("--horizon-days", type=int, default=20)
    args = parser.parse_args()

    signals = pd.read_csv(args.signals)
    stocks = pd.read_csv(args.stock_daily)

    tradable = signals[signals["decision"].isin(["A+ setup", "Tradable"])].copy()
    trades, summary = backtest_underlying_returns(tradable, stocks, args.horizon_days)

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    trades.to_csv(out_dir / "backtest_trades.csv", index=False)
    summary.to_csv(out_dir / "backtest_summary.csv", index=False)

    print(summary.to_string(index=False))
    print(f"Wrote backtest outputs to {out_dir}")


if __name__ == "__main__":
    main()
