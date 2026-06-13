"""SignalOS — Capital-Compounder screen dashboard (phone-first Streamlit).

Renders the merged screen: named patterns, Power Gauge, capital verdict, IV
regime, the risk-engine book summary, and propose-only agent cards.

Run:
    streamlit run app/screen_dashboard.py
"""
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.reporting import (
    screen_overview, screen_by_pattern, book_summary, proposal_cards,
)

SIGNALS_PATH = ROOT / "outputs" / "screen_signals.csv"

st.set_page_config(page_title="SignalOS — Capital Compounder", layout="centered")
st.title("SignalOS — Capital-Compounder Screen")
st.caption("Flow + Uniform-Accounting-lite + Power Gauge + IV regime + risk. "
           "Research only — not investment advice.")

if not SIGNALS_PATH.exists():
    st.warning("No screen output yet. Run: `python scripts/run_screen.py --demo`")
    st.stop()

signals = pd.read_csv(SIGNALS_PATH)

# --- Book risk summary ---
book = book_summary(signals)
st.subheader("Book risk")
c1, c2, c3 = st.columns(3)
c1.metric("Positions", int(book.get("positions", 0)))
c2.metric("Open risk", f"${book.get('open_risk', 0):,.0f}")
c3.metric("Heat", f"{book.get('heat_pct', 0) * 100:.2f}%")
g1, g2, g3, g4 = st.columns(4)
g1.metric("Net Δ", f"{book.get('net_delta', 0):,.0f}")
g2.metric("Net Γ", f"{book.get('net_gamma', 0):,.1f}")
g3.metric("Net Θ", f"{book.get('net_theta', 0):,.1f}")
g4.metric("Net V", f"{book.get('net_vega', 0):,.1f}")

# --- Screen patterns ---
st.subheader("Setups by screen")
patterns = screen_by_pattern(signals)
if patterns:
    order = ["COMPOUNDER_BREAKOUT", "DESTROYER_BREAKDOWN", "SQUEEZE",
             "PREMIUM_REVERSION", "FLOW_CONVERGENCE"]
    names = [n for n in order if n in patterns] + [n for n in patterns if n not in order]
    tabs = st.tabs(names)
    for tab, name in zip(tabs, names):
        with tab:
            st.dataframe(patterns[name], use_container_width=True, hide_index=True)
else:
    st.info("No named-screen setups in the current output.")

# --- Full ranked overview ---
st.subheader("All candidates (ranked)")
st.dataframe(screen_overview(signals), use_container_width=True, hide_index=True)

# --- Propose-only agent cards ---
st.subheader("Agent proposals (propose-only — no live orders)")
for card in proposal_cards(signals):
    with st.expander(
        f"{card['ticker']} · {card['screen']} · {card['contracts']} contracts · "
        f"${card['dollar_risk']:,.0f} risk"
    ):
        st.write(f"**Structure:** {card['structure']}")
        st.write(f"**Thesis:** {card['thesis']}")
        st.write(f"**Invalidation:** {card['invalidation']}")
        st.write(f"**Entry:** {card['entry_note']}")
        st.caption(f"Power Gauge {card['power_gauge_rating']} · "
                   f"{card['capital_verdict']} · IV {card['iv_regime']} · "
                   f"convergence {card['convergence_score']}")
