from pathlib import Path
import argparse
import os
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.data_sources.tradier_provider import TradierProvider
from signalos.data_sources.validation import validate_stock_daily, validate_option_chain
from signalos.pipeline import run_daily_scan


def load_universe(path: Path) -> list[str]:
    df = pd.read_csv(path)
    if "ticker" not in df.columns:
        raise ValueError("Universe file must include a ticker column")
    return sorted(df["ticker"].dropna().astype(str).str.upper().unique())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default=str(ROOT / "config" / "universe.csv"))
    parser.add_argument("--out-dir", default=str(ROOT / "data" / "live"))
    parser.add_argument("--lookback-days", type=int, default=320)
    parser.add_argument("--min-dte", type=int, default=14)
    parser.add_argument("--max-dte", type=int, default=90)
    parser.add_argument("--expirations-per-symbol", type=int, default=3)
    parser.add_argument("--sandbox", action="store_true")
    parser.add_argument("--scan", action="store_true", help="Run scanner after fetching data")
    args = parser.parse_args()

    token = os.getenv("TRADIER_TOKEN")
    if not token:
        raise SystemExit("Missing TRADIER_TOKEN. Set it locally, in Codespaces secrets, GitHub Actions secrets, or Streamlit secrets.")

    universe = load_universe(Path(args.universe))
    provider = TradierProvider(token=token, sandbox=args.sandbox)

    print(f"Fetching stock history for {len(universe)} symbols...")
    stock_daily = provider.fetch_stock_daily(universe, lookback_days=args.lookback_days)
    validate_stock_daily(stock_daily)

    print("Fetching option chains...")
    option_chain = provider.fetch_option_chains(
        universe,
        min_dte=args.min_dte,
        max_dte=args.max_dte,
        expirations_per_symbol=args.expirations_per_symbol,
    )
    validate_option_chain(option_chain)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stock_path = out_dir / "stock_daily.csv"
    option_path = out_dir / "option_chain_latest.csv"

    stock_daily.to_csv(stock_path, index=False)
    option_chain.to_csv(option_path, index=False)

    print(f"Wrote {len(stock_daily):,} stock rows to {stock_path}")
    print(f"Wrote {len(option_chain):,} option rows to {option_path}")

    if args.scan:
        signals = run_daily_scan(stock_daily, option_chain)
        outputs = ROOT / "outputs"
        outputs.mkdir(exist_ok=True)
        signals.to_csv(outputs / "daily_signals_live.csv", index=False)
        print(f"Wrote scan to {outputs / 'daily_signals_live.csv'}")
        print(signals[[
            "ticker", "bias", "decision", "convergence_score",
            "uoa_score", "money_flow_score", "liquidity_score",
            "reject_reason", "suggested_structure"
        ]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
