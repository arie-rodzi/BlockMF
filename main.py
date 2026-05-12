import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from data_generator import generate_borrowers
from scoring import calculate_scores
from blockchain import create_transaction

st.set_page_config(page_title="BlockMF", page_icon="⛓️", layout="wide")

CUSTOM_CSS = """
<style>
    .main {background: linear-gradient(135deg, #07111f 0%, #101827 50%, #14213d 100%);}
    h1, h2, h3, h4, p, label, span, div {font-family: 'Inter', sans-serif;}
    .hero {
        padding: 28px; border-radius: 24px;
        background: linear-gradient(120deg, rgba(15, 23, 42, .95), rgba(30, 41, 59, .88));
        border: 1px solid rgba(255,255,255,.10);
        box-shadow: 0 18px 45px rgba(0,0,0,.35);
    }
    .hero h1 {font-size: 46px; color: #f8fafc; margin-bottom: 6px;}
    .hero p {font-size: 17px; color: #cbd5e1;}
    .metric-card {
        padding: 20px; border-radius: 20px; background: rgba(255,255,255,.08);
        border: 1px solid rgba(255,255,255,.10); color: white;
        box-shadow: 0 12px 30px rgba(0,0,0,.20);
    }
    .metric-card h3 {font-size: 14px; color: #cbd5e1; margin:0;}
    .metric-card h2 {font-size: 30px; color: #facc15; margin:4px 0 0 0;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {border-radius: 14px; padding: 12px 18px; background: rgba(255,255,255,.08);}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_data
def load_data(n_my, n_mv, seed):
    df = generate_borrowers(n_my, n_mv, seed)
    return score_borrowers(df)

with st.sidebar:
    st.title("⚙️ BlockMF Control")
    n_my = st.slider("Malaysia synthetic borrowers", 100, 2000, 500, step=100)
    n_mv = st.slider("Maldives synthetic borrowers", 100, 2000, 500, step=100)
    seed = st.number_input("Random seed", min_value=1, value=42)
    country_filter = st.multiselect("Country", ["Malaysia", "Maldives"], default=["Malaysia", "Maldives"])
    decision_filter = st.multiselect("Decision", ["Approved", "Review", "Rejected"], default=["Approved", "Review", "Rejected"])

scored = load_data(n_my, n_mv, seed)
df = scored[scored["country"].isin(country_filter) & scored["decision"].isin(decision_filter)].copy()
ledger = build_ledger(df)

st.markdown("""
<div class="hero">
    <h1>BlockMF</h1>
    <p>Blockchain-enabled microfinance analytics platform for transparent social financing, social capital scoring, and Malaysia–Maldives validation.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    ("Borrowers", f"{len(df):,}"),
    ("Approval Rate", f"{(df['decision'].eq('Approved').mean()*100):.1f}%" if len(df) else "0%"),
    ("Avg Eligibility", f"{df['eligibility_score'].mean():.3f}" if len(df) else "0"),
    ("Avg Social Capital", f"{df['social_capital_score'].mean():.3f}" if len(df) else "0"),
    ("Ledger Blocks", f"{len(ledger):,}"),
]
for col, (label, value) in zip([c1,c2,c3,c4,c5], metrics):
    col.markdown(f"<div class='metric-card'><h3>{label}</h3><h2>{value}</h2></div>", unsafe_allow_html=True)

st.write("")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Executive Dashboard", "Borrower Scoring", "Blockchain Ledger", "Malaysia vs Maldives", "Research Export"])

with tab1:
    left, right = st.columns([1.2, 1])
    with left:
        fig = px.histogram(df, x="eligibility_score", color="country", nbins=35, title="Eligibility Score Distribution")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        decision_counts = df.groupby(["country", "decision"]).size().reset_index(name="count")
        fig2 = px.bar(decision_counts, x="country", y="count", color="decision", barmode="group", title="Decision Profile")
        fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(df, x="social_capital_score", y="eligibility_score", color="country", size="requested_loan",
                      hover_data=["borrower_id", "sector", "decision", "risk_level"], title="Social Capital vs Eligibility")
    fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("Top-ranked borrower eligibility list")
    show_cols = ["borrower_id", "country", "region", "sector", "monthly_income", "requested_loan", "social_capital_score", "eligibility_score", "risk_level", "decision"]
    st.dataframe(df[show_cols].head(100), use_container_width=True, hide_index=True)

    st.subheader("Explainable decision inspector")
    selected = st.selectbox("Select borrower", df["borrower_id"].head(200).tolist())
    row = df[df["borrower_id"] == selected].iloc[0]
    st.metric("Eligibility score", f"{row['eligibility_score']:.3f}")
    st.metric("Risk score", f"{row['risk_score']:.3f}")
    st.write("Decision:", row["decision"])
    st.write("Reasons:")
    for reason in explain_decision(row):
        st.write(f"- {reason}")

with tab3:
    st.subheader("Blockchain-style immutable transaction ledger")
    st.caption("This module simulates a blockchain ledger. The Solidity contract in /contracts can be connected through Web3.py in the next development phase.")
    st.dataframe(ledger, use_container_width=True, hide_index=True)
    if not ledger.empty:
        fig4 = px.bar(ledger.groupby("country")["amount"].sum().reset_index(), x="country", y="amount", title="Recorded Loan Value by Country")
        fig4.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.subheader("Malaysia vs Maldives validation analytics")
    summary = df.groupby("country").agg(
        borrowers=("borrower_id", "count"),
        approval_rate=("decision", lambda x: (x == "Approved").mean()),
        mean_eligibility=("eligibility_score", "mean"),
        mean_social_capital=("social_capital_score", "mean"),
        mean_risk=("risk_score", "mean"),
        mean_financial_access=("financial_access", "mean"),
    ).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)

    radar = go.Figure()
    categories = ["approval_rate", "mean_eligibility", "mean_social_capital", "mean_financial_access", "mean_risk"]
    for _, r in summary.iterrows():
        radar.add_trace(go.Scatterpolar(r=[r[c] for c in categories], theta=categories, fill="toself", name=r["country"]))
    radar.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0,1])), showlegend=True,
                        paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(radar, use_container_width=True)

with tab5:
    st.subheader("Research export")
    st.write("Download reproducible synthetic dataset and ledger for experiments, paper tables, and appendix material.")
    st.download_button("Download scored borrower dataset CSV", df.to_csv(index=False), "blockmf_scored_borrowers.csv", "text/csv")
    st.download_button("Download blockchain ledger CSV", ledger.to_csv(index=False), "blockmf_ledger.csv", "text/csv")
    st.code("streamlit run app/main.py", language="bash")
