from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.pipeline import run_daily_scan
from signalos.backtest.simulator import backtest_underlying_returns


st.set_page_config(page_title="SignalOS Convergence Engine", layout="wide")

st.title("SignalOS Convergence Engine")
st.caption("Unusual options activity + money-flow confirmation + explicit reject reasons.")

stock_path = ROOT / "data" / "demo" / "stock_daily.csv"
option_path = ROOT / "data" / "demo" / "option_chain_latest.csv"

if not stock_path.exists() or not option_path.exists():
    st.warning("Demo data not found. Run: python scripts/make_demo_data.py")
    st.stop()

stock_daily = pd.read_csv(stock_path)
option_chain = pd.read_csv(option_path)
signals = run_daily_scan(stock_daily, option_chain)

tab1, tab2, tab3, tab4 = st.tabs(["Daily Signals", "Rejected UOA", "Ticker Drilldown", "Backtest"])

with tab1:
    st.subheader("Confirmed and Watchlist Signals")
    selected = signals[signals["decision"].isin(["A+ setup", "Tradable", "Watchlist"])]
    st.dataframe(
        selected[[
            "ticker", "bias", "decision", "convergence_score", "uoa_score",
            "money_flow_score", "trend_score", "rs_score", "liquidity_score",
            "suggested_structure", "reject_reason"
        ]],
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.subheader("Rejected High-UOA Signals")
    rejected = signals[signals["decision"].eq("Reject")]
    st.dataframe(
        rejected[[
            "ticker", "bias", "convergence_score", "uoa_score", "money_flow_score",
            "liquidity_score", "reject_reason", "option_symbol"
        ]],
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("Ticker Drilldown")
    tickers = sorted(signals["ticker"].unique())
    ticker = st.selectbox("Ticker", tickers)
    s = signals[signals["ticker"].eq(ticker)]
    st.dataframe(s, use_container_width=True, hide_index=True)

    chart_df = stock_daily[stock_daily["ticker"].eq(ticker)].copy()
    chart_df["date"] = pd.to_datetime(chart_df["date"])
    chart_df = chart_df.sort_values("date").set_index("date")
    st.line_chart(chart_df[["close"]])

with tab4:
    st.subheader("Underlying Return Backtest")
    horizon = st.slider("Forward horizon, trading days", 5, 60, 20, 5)
    tradable = signals[signals["decision"].isin(["A+ setup", "Tradable"])].copy()
    trades, summary = backtest_underlying_returns(tradable, stock_daily, horizon_days=horizon)

    st.write("Summary")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.write("Trades")
    if not trades.empty:
        st.dataframe(
            trades[[
                "ticker", "bias", "decision", "convergence_score", "close",
                "future_close", "forward_return", "bias_adjusted_return"
            ]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No trades with available forward-return data.")
