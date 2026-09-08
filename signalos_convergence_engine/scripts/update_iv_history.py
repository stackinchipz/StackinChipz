"""Append today's ATM IV snapshot to the IV-history store.

Run this daily (after fetching the option chain) so `iv_regime` can compute a
true 52-week IV rank instead of the cross-sectional fallback.

    python scripts/update_iv_history.py --option-chain data/live/option_chain_latest.csv
    python scripts/update_iv_history.py --demo
"""
from pathlib import Path
import argparse
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.data_sources.iv_store import append_iv_snapshot, load_iv_history


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true")
    p.add_argument("--option-chain", default=None)
    p.add_argument("--store", default=str(ROOT / "data" / "live" / "iv_history.csv"))
    args = p.parse_args()

    chain_path = (ROOT / "data" / "demo" / "option_chain_latest.csv") if args.demo else Path(args.option_chain)
    if not chain_path or not Path(chain_path).exists():
        raise SystemExit("Provide --demo or --option-chain <path>")

    chain = pd.read_csv(chain_path)
    store = append_iv_snapshot(chain, args.store)
    hist = load_iv_history(store)
    print(f"Appended snapshot to {store}")
    print(f"Store now holds {len(hist)} rows across {hist['ticker'].nunique()} tickers.")


if __name__ == "__main__":
    main()
