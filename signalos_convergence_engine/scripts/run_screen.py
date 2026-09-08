"""Run the full Capital-Compounder screen (flow + fundamentals + IV + risk).

Examples
--------
Offline demo (no network/keys):
    python scripts/run_screen.py --demo

Live, EDGAR fundamentals (needs egress to sec.gov; set a contact UA):
    python scripts/run_screen.py \
        --stock-daily data/live/stock_daily.csv \
        --option-chain data/live/option_chain_latest.csv \
        --fundamentals-provider edgar \
        --edgar-ua "SignalOS research you@email.com"

Live, Tradier/Morningstar fundamentals (uses TRADIER_TOKEN):
    python scripts/run_screen.py \
        --stock-daily data/live/stock_daily.csv \
        --option-chain data/live/option_chain_latest.csv \
        --fundamentals-provider tradier
"""
from pathlib import Path
import argparse
import os
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.pipeline_screen import run_full_screen, size_screen
from signalos.data_sources.fundamentals import load_fundamentals
from signalos.data_sources.expert_data import load_expert_signals


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true", help="Use data/demo CSVs + demo fundamentals")
    p.add_argument("--stock-daily", default=None)
    p.add_argument("--option-chain", default=None)
    p.add_argument("--fundamentals-provider", default="demo",
                   choices=["demo", "csv", "edgar", "tradier"])
    p.add_argument("--fundamentals-csv", default=None)
    p.add_argument("--edgar-ua", default=os.environ.get("EDGAR_USER_AGENT"))
    args = p.parse_args()

    expert_inputs = None
    if args.demo:
        stock_path = ROOT / "data" / "demo" / "stock_daily.csv"
        option_path = ROOT / "data" / "demo" / "option_chain_latest.csv"
        provider = "csv"
        fund_csv = ROOT / "data" / "demo" / "fundamentals.csv"
        expert_csv = ROOT / "data" / "demo" / "expert_inputs.csv"
        if expert_csv.exists():
            expert_inputs = load_expert_signals(provider="csv", csv_path=expert_csv)
    else:
        if not args.stock_daily or not args.option_chain:
            raise SystemExit("Provide --demo or both --stock-daily and --option-chain")
        stock_path = Path(args.stock_daily)
        option_path = Path(args.option_chain)
        provider = args.fundamentals_provider
        fund_csv = args.fundamentals_csv

    stock_daily = pd.read_csv(stock_path)
    option_chain = pd.read_csv(option_path)
    tickers = sorted(option_chain["ticker"].astype(str).str.upper().unique())

    fundamentals = load_fundamentals(
        provider=provider,
        tickers=tickers,
        csv_path=fund_csv,
        tradier_token=os.environ.get("TRADIER_TOKEN"),
        edgar_user_agent=args.edgar_ua,
    )

    sector_map = None
    universe_path = ROOT / "config" / "universe.csv"
    if universe_path.exists():
        sector_map = pd.read_csv(universe_path)
        sector_map = sector_map.rename(columns={c: c.lower() for c in sector_map.columns})
        if "ticker" in sector_map.columns:
            sector_map["ticker"] = sector_map["ticker"].str.upper()

    signals = run_full_screen(stock_daily, option_chain, fundamentals=fundamentals,
                              sector_map=sector_map, expert_inputs=expert_inputs)
    sized = size_screen(signals)

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    signals.to_csv(out_dir / "screen_signals.csv", index=False)
    if sized is not None and not sized.empty:
        sized.to_csv(out_dir / "screen_sized.csv", index=False)

    show = [c for c in [
        "ticker", "bias", "decision", "screen", "convergence_score",
        "power_gauge_rating", "capital_verdict", "capital_efficiency_score",
        "iv_regime", "screen_structure",
    ] if c in signals.columns]
    print(f"\nWrote {len(signals)} screened rows to {out_dir/'screen_signals.csv'}\n")
    print(signals[show].head(25).to_string(index=False))

    if sized is not None and not sized.empty and "book" in sized.attrs:
        b = sized.attrs["book"]
        print("\n=== Book risk summary ===")
        print(f"Positions: {b['positions']}  Open risk: ${b['open_risk']:,.0f} "
              f"({b['heat_pct']*100:.2f}% heat)")
        print(f"Net Greeks  Δ {b['net_delta']:,.0f}  Γ {b['net_gamma']:,.2f}  "
              f"Θ {b['net_theta']:,.2f}  V {b['net_vega']:,.2f}")


if __name__ == "__main__":
    main()
