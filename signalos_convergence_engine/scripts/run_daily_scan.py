from pathlib import Path
import argparse
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.pipeline import run_daily_scan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Use data/demo CSVs")
    parser.add_argument("--stock-daily", default=None)
    parser.add_argument("--option-chain", default=None)
    args = parser.parse_args()

    if args.demo:
        stock_path = ROOT / "data" / "demo" / "stock_daily.csv"
        option_path = ROOT / "data" / "demo" / "option_chain_latest.csv"
    else:
        if not args.stock_daily or not args.option_chain:
            raise SystemExit("Provide --demo or both --stock-daily and --option-chain")
        stock_path = Path(args.stock_daily)
        option_path = Path(args.option_chain)

    stock_daily = pd.read_csv(stock_path)
    option_chain = pd.read_csv(option_path)

    signals = run_daily_scan(stock_daily, option_chain)

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)

    signals.to_csv(out_dir / "daily_signals.csv", index=False)
    signals[signals["decision"].eq("Reject")].to_csv(out_dir / "rejected_uoa_signals.csv", index=False)

    cols = [
        "ticker", "bias", "decision", "convergence_score", "uoa_score",
        "money_flow_score", "liquidity_score", "reject_reason", "suggested_structure"
    ]
    print(f"Wrote {len(signals)} signals to {out_dir / 'daily_signals.csv'}")
    print(signals[cols].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
