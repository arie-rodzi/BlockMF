import numpy as np
import pandas as pd


def calculate_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate social capital, risk, eligibility score, decision and priority ranking."""
    df = df.copy()

    # Financial ratios
    df["debt_to_income"] = (df["monthly_debt"] / df["monthly_income"]).clip(0, 2)
    df["loan_to_income"] = (df["loan_amount"] / df["monthly_income"]).clip(0, 10)

    # Social capital score
    df["social_capital_score"] = (
        0.35 * df["community_score"]
        + 0.35 * df["trust_rating"]
        + 0.30 * df["repayment_history"]
    ).clip(0, 1)

    # Financial resilience score
    df["financial_resilience_score"] = (
        0.40 * (1 - (df["debt_to_income"] / 2))
        + 0.30 * (1 - (df["loan_to_income"] / 10))
        + 0.30 * df["financial_access_index"]
    ).clip(0, 1)

    # Digital outreach score
    df["outreach_score"] = (
        0.55 * df["digital_access"]
        + 0.45 * df["financial_access_index"]
    ).clip(0, 1)

    # Risk score: lower is better
    df["risk_score"] = (
        0.45 * df["debt_to_income"].clip(0, 1)
        + 0.30 * (1 - df["repayment_history"])
        + 0.25 * (1 - df["trust_rating"])
    ).clip(0, 1)

    # Eligibility score: higher is better
    df["eligibility_score"] = (
        0.40 * df["social_capital_score"]
        + 0.30 * df["financial_resilience_score"]
        + 0.20 * df["repayment_history"]
        + 0.10 * df["outreach_score"]
    ).clip(0, 1)

    conditions = [
        df["eligibility_score"] >= 0.75,
        df["eligibility_score"] >= 0.60,
        df["eligibility_score"] >= 0.45,
    ]
    choices = ["Approved", "Review", "Conditional"]
    df["decision"] = np.select(conditions, choices, default="Rejected")

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-0.01, 0.33, 0.66, 1.01],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    df["priority_rank"] = df["eligibility_score"].rank(ascending=False, method="dense").astype(int)

    return df.sort_values("priority_rank").reset_index(drop=True)


def explain_decision(row: pd.Series) -> str:
    """Generate simple explainable decision text for one borrower."""
    reasons = []

    if row["social_capital_score"] >= 0.75:
        reasons.append("strong social capital")
    if row["repayment_history"] >= 0.75:
        reasons.append("good repayment history")
    if row["debt_to_income"] <= 0.35:
        reasons.append("manageable debt burden")
    if row["financial_access_index"] < 0.45:
        reasons.append("limited financial access, indicating outreach need")
    if row["risk_score"] >= 0.66:
        reasons.append("high repayment risk")

    if not reasons:
        reasons.append("balanced financial and social profile")

    return "Decision is based on " + ", ".join(reasons) + "."