from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.pipeline import run_daily_scan
from signalos.backtest.simulator import backtest_underlying_returns


st.set_page_config(
    page_title="SignalOS Mobile",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
        max-width: 720px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem;
    }
    .signal-card {
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 14px;
        padding: 14px 14px 10px 14px;
        margin-bottom: 12px;
        background: rgba(255,255,255,0.035);
    }
    .signal-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 2px;
    }
    .pill {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 999px;
        font-size: 0.78rem;
        margin-right: 4px;
        margin-bottom: 4px;
        border: 1px solid rgba(255,255,255,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data():
    live_stock_path = ROOT / "data" / "live" / "stock_daily.csv"
    live_option_path = ROOT / "data" / "live" / "option_chain_latest.csv"
    demo_stock_path = ROOT / "data" / "demo" / "stock_daily.csv"
    demo_option_path = ROOT / "data" / "demo" / "option_chain_latest.csv"

    if live_stock_path.exists() and live_option_path.exists():
        stock_path = live_stock_path
        option_path = live_option_path
        mode = "live"
    else:
        stock_path = demo_stock_path
        option_path = demo_option_path
        mode = "demo"

    if not stock_path.exists() or not option_path.exists():
        raise FileNotFoundError("No data found. Run demo generation or live data fetch first.")

    stocks = pd.read_csv(stock_path)
    options = pd.read_csv(option_path)
    signals = run_daily_scan(stocks, options)
    return stocks, options, signals, mode


def badge(decision):
    if decision == "A+ setup":
        return "🟢"
    if decision == "Tradable":
        return "🔵"
    if decision == "Watchlist":
        return "🟡"
    return "🔴"


def fmt(value, default="N/A"):
    if pd.isna(value):
        return default
    return value


def render_card(row):
    title = f"{badge(row['decision'])} {row['ticker']} — {row['bias']}"
    reject = fmt(row.get("reject_reason", "None"), "None")
    if reject == "None" or reject == "":
        reject = "None"

    st.markdown('<div class="signal-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="signal-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <span class="pill">{row['decision']}</span>
        <span class="pill">Score {row['convergence_score']:.1f}</span>
        <span class="pill">UOA {row['uoa_score']:.1f}</span>
        <span class="pill">MF {row['money_flow_score']:.1f}</span>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
**Structure:** {fmt(row.get('suggested_structure'))}  
**Reject:** {reject}  
**Option:** `{fmt(row.get('option_symbol'))}`  
**Bid / Ask / Mid:** {fmt(row.get('bid'))} / {fmt(row.get('ask'))} / {fmt(row.get('mid'))}  
**DTE / Delta / IV:** {fmt(row.get('days_to_expiration'))} / {fmt(row.get('delta'))} / {fmt(row.get('implied_volatility'))}
        """
    )
    with st.expander("Risk rules"):
        st.write(fmt(row.get("risk_rules"), "N/A"))
    st.markdown("</div>", unsafe_allow_html=True)


try:
    stocks, options, signals, data_mode = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

st.title("SignalOS")
st.caption("Mobile command center: convergence signals, rejects, and trade prep.")

last_date = signals["date"].max()
tradable_count = int(signals["decision"].isin(["A+ setup", "Tradable"]).sum())
watchlist_count = int(signals["decision"].eq("Watchlist").sum())
reject_count = int(signals["decision"].eq("Reject").sum())

c1, c2, c3 = st.columns(3)
c1.metric("Trade", tradable_count)
c2.metric("Watch", watchlist_count)
c3.metric("Reject", reject_count)

st.caption(f"Signal date: {last_date} · Data mode: {data_mode.upper()}")

try:
    mode = st.segmented_control(
        "View",
        ["Trade", "Watchlist", "Rejected", "Drilldown", "Backtest"],
        default="Trade",
    )
except Exception:
    mode = st.radio(
        "View",
        ["Trade", "Watchlist", "Rejected", "Drilldown", "Backtest"],
        horizontal=True,
    )

if mode == "Trade":
    st.subheader("Trade candidates")
    subset = signals[signals["decision"].isin(["A+ setup", "Tradable"])].copy()
    if subset.empty:
        st.info("No confirmed trade candidates.")
    else:
        max_cards = st.slider("Cards", 3, min(20, len(subset)), min(8, len(subset)))
        for _, row in subset.head(max_cards).iterrows():
            render_card(row)

elif mode == "Watchlist":
    st.subheader("Watchlist")
    subset = signals[signals["decision"].eq("Watchlist")].copy()
    if subset.empty:
        st.info("No watchlist signals.")
    else:
        for _, row in subset.head(15).iterrows():
            render_card(row)

elif mode == "Rejected":
    st.subheader("Rejected UOA")
    st.caption("These are valuable. This is where the system protects you.")
    subset = signals[signals["decision"].eq("Reject")].copy()
    if subset.empty:
        st.info("No rejected signals.")
    else:
        for _, row in subset.head(15).iterrows():
            render_card(row)

elif mode == "Drilldown":
    st.subheader("Ticker drilldown")
    ticker = st.selectbox("Ticker", sorted(signals["ticker"].unique()))
    signal_rows = signals[signals["ticker"].eq(ticker)]
    st.dataframe(
        signal_rows[[
            "ticker", "bias", "decision", "convergence_score", "uoa_score",
            "money_flow_score", "liquidity_score", "reject_reason",
            "suggested_structure"
        ]],
        use_container_width=True,
        hide_index=True,
    )

    chart_df = stocks[stocks["ticker"].eq(ticker)].copy()
    chart_df["date"] = pd.to_datetime(chart_df["date"])
    chart_df = chart_df.sort_values("date").set_index("date")
    st.line_chart(chart_df[["close"]])

elif mode == "Backtest":
    st.subheader("Backtest snapshot")
    horizon = st.slider("Forward horizon", 5, 60, 20, 5)
    tradable = signals[signals["decision"].isin(["A+ setup", "Tradable"])].copy()
    trades, summary = backtest_underlying_returns(tradable, stocks, horizon_days=horizon)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    if not trades.empty:
        st.dataframe(
            trades[[
                "ticker", "bias", "decision", "convergence_score",
                "forward_return", "bias_adjusted_return"
            ]],
            use_container_width=True,
            hide_index=True,
        )

st.divider()

csv = signals.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download daily signals CSV",
    data=csv,
    file_name="signalos_daily_signals.csv",
    mime="text/csv",
    use_container_width=True,
)

st.caption("Execution checklist: confirm in thinkorswim, check spread, use limit orders, defined-risk only, journal every trade.")
