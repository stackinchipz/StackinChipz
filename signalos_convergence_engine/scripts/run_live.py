"""One-command live pipeline: Tradier data -> screen -> proposals (-> preview).

Once your .env is filled in (TRADIER_TOKEN, TRADIER_ACCOUNT_ID, TRADIER_ENV,
EDGAR_USER_AGENT), this does the whole loop:

    fetch Tradier stock + option data
      -> EDGAR fundamentals (free)
      -> full Capital-Compounder screen
      -> risk-engine sizing + propose-only agent
      -> append IV history
      -> (optional) Tradier preview of the top options proposals (sends nothing)

Usage:
    set -a; source .env; set +a
    python scripts/run_live.py                 # screen + proposals
    python scripts/run_live.py --preview 5      # + Tradier preview of top 5 (no orders placed)

Nothing is ever PLACED by this script. Preview uses Tradier preview=true.
"""
from pathlib import Path
import argparse
import os
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.data_sources.tradier_provider import TradierProvider
from signalos.data_sources.validation import validate_stock_daily, validate_option_chain
from signalos.data_sources.fundamentals import load_fundamentals
from signalos.data_sources.iv_store import append_iv_snapshot
from signalos.pipeline_screen import run_full_screen, size_screen
from signalos.agent import run_agent, TradierBroker


def load_universe(path: Path) -> list[str]:
    df = pd.read_csv(path)
    return sorted(df["ticker"].dropna().astype(str).str.upper().unique())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--universe", default=str(ROOT / "config" / "universe.csv"))
    p.add_argument("--lookback-days", type=int, default=320)
    p.add_argument("--min-dte", type=int, default=14)
    p.add_argument("--max-dte", type=int, default=90)
    p.add_argument("--preview", type=int, default=0, metavar="N",
                   help="Tradier-preview the top N options proposals (places nothing)")
    args = p.parse_args()

    token = os.getenv("TRADIER_TOKEN")
    if not token:
        raise SystemExit("Missing TRADIER_TOKEN. Fill in .env and `set -a; source .env; set +a`.")
    sandbox = os.getenv("TRADIER_ENV", "sandbox").lower() != "live"
    print(f"[1/6] Tradier {'SANDBOX' if sandbox else 'LIVE'} — fetching data...")

    universe = load_universe(Path(args.universe))
    provider = TradierProvider(token=token, sandbox=sandbox)
    stock_daily = provider.fetch_stock_daily(universe, lookback_days=args.lookback_days)
    validate_stock_daily(stock_daily)
    option_chain = provider.fetch_option_chains(universe, min_dte=args.min_dte, max_dte=args.max_dte)
    validate_option_chain(option_chain)
    live = ROOT / "data" / "live"
    live.mkdir(parents=True, exist_ok=True)
    stock_daily.to_csv(live / "stock_daily.csv", index=False)
    option_chain.to_csv(live / "option_chain_latest.csv", index=False)
    print(f"      {len(stock_daily):,} stock rows, {len(option_chain):,} option rows.")

    # Fundamentals (EDGAR free). Non-fatal if it fails -> capital layer neutral.
    print("[2/6] EDGAR fundamentals...")
    fundamentals = None
    try:
        tickers = sorted(option_chain["ticker"].astype(str).str.upper().unique())
        fundamentals = load_fundamentals("edgar", tickers=tickers,
                                         edgar_user_agent=os.getenv("EDGAR_USER_AGENT"))
        print(f"      fundamentals for {fundamentals['ticker'].nunique()} tickers.")
    except Exception as e:
        print(f"      WARN: EDGAR fetch failed ({e}); running without fundamentals "
              "(capital-efficiency = neutral).")

    print("[3/6] Running full screen...")
    sector_map = pd.read_csv(ROOT / "config" / "universe.csv").rename(columns=str.lower)
    sector_map["ticker"] = sector_map["ticker"].str.upper()
    signals = run_full_screen(stock_daily, option_chain, fundamentals=fundamentals,
                              sector_map=sector_map)
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    signals.to_csv(out / "screen_signals.csv", index=False)

    print("[4/6] Sizing + propose-only agent...")
    agent_out = run_agent(signals, audit_path=out / "agent_proposals.jsonl")
    book = agent_out["book"]

    print("[5/6] Appending IV history...")
    append_iv_snapshot(option_chain, live / "iv_history.csv")

    # Summary.
    show = [c for c in ["ticker", "bias", "decision", "screen", "convergence_score",
                        "power_gauge_rating", "capital_verdict", "iv_regime",
                        "screen_structure"] if c in signals.columns]
    print("\n=== Top screened setups ===")
    print(signals[show].head(15).to_string(index=False))
    if book:
        print(f"\nBook: {book.get('positions',0)} positions, ${book.get('open_risk',0):,.0f} "
              f"open risk ({book.get('heat_pct',0)*100:.2f}% heat) | "
              f"Net Δ {book.get('net_delta',0):,.0f}  V {book.get('net_vega',0):,.1f}")

    print("[6/6] Done. Proposals -> outputs/agent_proposals.jsonl")

    if args.preview:
        acct = os.getenv("TRADIER_ACCOUNT_ID")
        if not acct:
            print("\nSkip preview: set TRADIER_ACCOUNT_ID to preview orders.")
            return
        broker = TradierBroker(token=token, account_id=acct, sandbox=sandbox, armed=True)
        sized = [r for r in agent_out["proposals"] if r["contracts"] > 0][: args.preview]
        print(f"\n=== Tradier preview (top {len(sized)}, NOTHING placed) ===")
        for r in sized:
            try:
                pv = broker.preview(r)
                print(f"{r['ticker']:5} {r['structure']:42} -> {pv['status']}: {pv.get('result')}")
            except Exception as e:
                print(f"{r['ticker']:5} preview error: {e}")


if __name__ == "__main__":
    main()
