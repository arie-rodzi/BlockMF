import numpy as np
import pandas as pd


def minmax(series: pd.Series) -> pd.Series:
    span = series.max() - series.min()
    if span == 0:
        return pd.Series(np.ones(len(series)), index=series.index)
    return (series - series.min()) / span


def score_borrowers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["disposable_income"] = out["monthly_income"] - out["monthly_expenses"] - out["existing_debt"]
    out["debt_burden"] = out["existing_debt"] / out["monthly_income"].replace(0, np.nan)
    out["loan_to_income"] = out["requested_loan"] / out["monthly_income"].replace(0, np.nan)

    disposable = minmax(out["disposable_income"])
    debt_score = 1 - minmax(out["debt_burden"].fillna(0))
    loan_score = 1 - minmax(out["loan_to_income"].fillna(0))

    out["social_capital_score"] = (
        0.40 * out["trust_score"] +
        0.25 * out["community_participation"] +
        0.20 * out["repayment_history"] +
        0.15 * out["financial_access"]
    )

    out["eligibility_score"] = (
        0.30 * out["social_capital_score"] +
        0.25 * disposable +
        0.20 * debt_score +
        0.15 * loan_score +
        0.10 * out["internet_access"]
    ).clip(0, 1)

    out["risk_score"] = (1 - out["eligibility_score"]).clip(0, 1)
    out["decision"] = np.where(out["eligibility_score"] >= 0.68, "Approved",
                         np.where(out["eligibility_score"] >= 0.52, "Review", "Rejected"))
    out["risk_level"] = np.where(out["risk_score"] <= 0.32, "Low",
                          np.where(out["risk_score"] <= 0.48, "Medium", "High"))
    return out.sort_values("eligibility_score", ascending=False).reset_index(drop=True)


def explain_decision(row: pd.Series) -> list[str]:
    reasons = []
    if row["social_capital_score"] >= 0.70:
        reasons.append("strong social capital profile")
    if row["repayment_history"] >= 0.70:
        reasons.append("positive repayment history")
    if row["debt_burden"] <= 0.25:
        reasons.append("manageable debt burden")
    if row["financial_access"] < 0.50:
        reasons.append("financial access gap indicates outreach need")
    if row["loan_to_income"] > 2.0:
        reasons.append("requested loan is relatively high against income")
    return reasons or ["balanced financial and social indicators"]
