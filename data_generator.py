import numpy as np
import pandas as pd


def generate_borrowers(n_malaysia: int = 500, n_maldives: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    rows = []
    sectors_my = ["micro SME", "small retail", "agriculture", "food business", "gig work"]
    sectors_mv = ["fisheries", "island retail", "tourism microservice", "boat service", "home enterprise"]

    for i in range(n_malaysia):
        income = np.clip(rng.normal(2600, 700), 900, 6500)
        expenses = income * rng.uniform(0.45, 0.82)
        debt = rng.uniform(100, 1400)
        requested = rng.uniform(800, 5000)
        trust = rng.beta(7, 3)
        community = rng.beta(6, 4)
        access = rng.beta(7, 3)
        repayment_history = rng.beta(8, 3)
        rows.append({
            "borrower_id": f"MY-{i+1:04d}",
            "country": "Malaysia",
            "region": rng.choice(["Urban", "Semi-urban", "Rural"]),
            "sector": rng.choice(sectors_my),
            "monthly_income": round(income, 2),
            "monthly_expenses": round(expenses, 2),
            "existing_debt": round(debt, 2),
            "requested_loan": round(requested, 2),
            "trust_score": round(trust, 3),
            "community_participation": round(community, 3),
            "financial_access": round(access, 3),
            "repayment_history": round(repayment_history, 3),
            "internet_access": round(rng.beta(8, 2), 3),
        })

    for i in range(n_maldives):
        income = np.clip(rng.normal(9800, 2600), 3500, 22000)  # MVR-inspired synthetic values
        expenses = income * rng.uniform(0.50, 0.88)
        debt = rng.uniform(500, 4800)
        requested = rng.uniform(3000, 18000)
        trust = rng.beta(6, 4)
        community = rng.beta(7, 3)
        access = rng.beta(5, 5)
        repayment_history = rng.beta(7, 4)
        rows.append({
            "borrower_id": f"MV-{i+1:04d}",
            "country": "Maldives",
            "region": rng.choice(["Male", "Atoll centre", "Outer island"]),
            "sector": rng.choice(sectors_mv),
            "monthly_income": round(income, 2),
            "monthly_expenses": round(expenses, 2),
            "existing_debt": round(debt, 2),
            "requested_loan": round(requested, 2),
            "trust_score": round(trust, 3),
            "community_participation": round(community, 3),
            "financial_access": round(access, 3),
            "repayment_history": round(repayment_history, 3),
            "internet_access": round(rng.beta(6, 4), 3),
        })

    return pd.DataFrame(rows)
