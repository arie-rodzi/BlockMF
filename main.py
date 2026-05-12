import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="BlockMF",
    page_icon="🔗",
    layout="wide",
)


def load_data():
    import data_generator
    import scoring

    df = data_generator.generate_borrowers()
    df = scoring.calculate_scores(df)
    return df


def build_ledger(df):
    import ledger

    return ledger.generate_ledger(df)


def show_header():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            color: #0B1F3A;
            margin-bottom: 0px;
        }
        .subtitle {
            font-size: 18px;
            color: #4B5563;
            margin-top: 0px;
        }
        .metric-card {
            padding: 18px;
            border-radius: 18px;
            background: linear-gradient(135deg, #F8FAFC, #EEF2FF);
            border: 1px solid #E5E7EB;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="main-title">BlockMF</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Blockchain-enabled Microfinance Analytics Platform for Social Capital Outreach</div>',
        unsafe_allow_html=True,
    )


def main():
    show_header()

    with st.spinner("Generating synthetic Malaysia–Maldives borrower data..."):
        df = load_data()
        ledger_df = build_ledger(df)

    st.sidebar.title("BlockMF Controls")
    country_filter = st.sidebar.multiselect(
        "Country",
        sorted(df["country"].unique()),
        default=sorted(df["country"].unique()),
    )
    decision_filter = st.sidebar.multiselect(
        "Decision",
        sorted(df["decision"].unique()),
        default=sorted(df["decision"].unique()),
    )
    risk_filter = st.sidebar.multiselect(
        "Risk Level",
        sorted(df["risk_level"].unique()),
        default=sorted(df["risk_level"].unique()),
    )

    filtered = df[
        (df["country"].isin(country_filter))
        & (df["decision"].isin(decision_filter))
        & (df["risk_level"].isin(risk_filter))
    ].copy()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Executive Dashboard",
            "Borrower Scoring",
            "Blockchain Ledger",
            "Malaysia vs Maldives",
        ]
    )

    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Borrowers", f"{len(filtered):,}")
        col2.metric("Average Eligibility", f"{filtered['eligibility_score'].mean():.3f}")
        col3.metric("Approval Rate", f"{(filtered['decision'].eq('Approved').mean() * 100):.1f}%")
        col4.metric("Verified Transactions", f"{len(ledger_df):,}")

        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(
                filtered,
                x="eligibility_score",
                color="country",
                nbins=30,
                title="Eligibility Score Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            summary = filtered.groupby(["country", "decision"]).size().reset_index(name="count")
            fig = px.bar(
                summary,
                x="country",
                y="count",
                color="decision",
                barmode="group",
                title="Decision Summary by Country",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top Priority Borrowers")
        st.dataframe(
            filtered[
                [
                    "priority_rank",
                    "borrower_id",
                    "country",
                    "sector",
                    "loan_amount",
                    "social_capital_score",
                    "eligibility_score",
                    "risk_level",
                    "decision",
                ]
            ].head(15),
            use_container_width=True,
        )

    with tab2:
        st.subheader("Borrower Scoring and Explainable Decision")

        selected_id = st.selectbox("Select borrower", filtered["borrower_id"].tolist())
        row = filtered[filtered["borrower_id"] == selected_id].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Eligibility", f"{row['eligibility_score']:.3f}")
        col2.metric("Social Capital", f"{row['social_capital_score']:.3f}")
        col3.metric("Risk Score", f"{row['risk_score']:.3f}")
        col4.metric("Decision", row["decision"])

        import scoring
        st.info(scoring.explain_decision(row))

        st.dataframe(pd.DataFrame(row).T, use_container_width=True)

    with tab3:
        st.subheader("Blockchain-Style Verification Ledger")
        st.caption("This starter version uses hash-based transaction simulation. It can later be connected to Ganache, Solidity and Web3.py.")

        st.dataframe(ledger_df, use_container_width=True)

        csv = ledger_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Ledger CSV",
            csv,
            "blockmf_ledger.csv",
            "text/csv",
        )

    with tab4:
        st.subheader("Malaysia vs Maldives Comparative Analytics")

        country_summary = (
            df.groupby("country")
            .agg(
                borrowers=("borrower_id", "count"),
                avg_income=("monthly_income", "mean"),
                avg_loan=("loan_amount", "mean"),
                avg_social_capital=("social_capital_score", "mean"),
                avg_eligibility=("eligibility_score", "mean"),
                avg_risk=("risk_score", "mean"),
                approval_rate=("decision", lambda x: (x == "Approved").mean()),
            )
            .reset_index()
        )

        st.dataframe(country_summary, use_container_width=True)

        fig = px.bar(
            country_summary,
            x="country",
            y=["avg_social_capital", "avg_eligibility", "avg_risk", "approval_rate"],
            barmode="group",
            title="Comparative Microfinance Indicators",
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.scatter(
            df,
            x="social_capital_score",
            y="eligibility_score",
            color="country",
            size="loan_amount",
            hover_data=["borrower_id", "sector", "decision", "risk_level"],
            title="Social Capital vs Eligibility Score",
        )
        st.plotly_chart(fig2, use_container_width=True)


if __name__ == "__main__":
    main()