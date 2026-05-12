import numpy as np
import pandas as pd


def generate_borrowers(n_malaysia: int = 300, n_maldives: int = 300, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic borrower data for Malaysia and Maldives."""
    rng = np.random.default_rng(seed)

    def make_country(country: str, n: int) -> pd.DataFrame:
        if country == "Malaysia":
            income = rng.normal(2600, 850, n).clip(800, 8000)
            debt = rng.normal(650, 350, n).clip(0, 3000)
            loan_amount = rng.normal(3500, 1200, n).clip(500, 10000)
            access = rng.normal(0.68, 0.16, n).clip(0.15, 1.0)
            sectors = rng.choice(
                ["Micro-SME", "Retail", "Food", "Agriculture", "Services"],
                n,
                p=[0.30, 0.22, 0.18, 0.15, 0.15],
            )
            locations = rng.choice(
                ["Urban", "Semi-urban", "Rural"],
                n,
                p=[0.40, 0.35, 0.25],
            )
        else:
            income = rng.normal(7000, 2300, n).clip(1800, 18000)
            debt = rng.normal(1600, 800, n).clip(0, 7000)
            loan_amount = rng.normal(9000, 3000, n).clip(1500, 25000)
            access = rng.normal(0.50, 0.20, n).clip(0.10, 1.0)
            sectors = rng.choice(
                ["Tourism", "Fisheries", "Island Retail", "Food", "Services"],
                n,
                p=[0.28, 0.24, 0.20, 0.14, 0.14],
            )
            locations = rng.choice(
                ["Capital", "Regional Island", "Remote Island"],
                n,
                p=[0.25, 0.45, 0.30],
            )

        trust = rng.normal(0.72, 0.14, n).clip(0.20, 1.0)
        community = rng.normal(0.66, 0.17, n).clip(0.10, 1.0)
        repayment_history = rng.normal(0.70, 0.18, n).clip(0.05, 1.0)
        digital_access = (access + rng.normal(0, 0.10, n)).clip(0.05, 1.0)

        return pd.DataFrame(
            {
                "borrower_id": [f"{country[:3].upper()}-{i+1:04d}" for i in range(n)],
                "country": country,
                "location_type": locations,
                "sector": sectors,
                "monthly_income": np.round(income, 2),
                "monthly_debt": np.round(debt, 2),
                "loan_amount": np.round(loan_amount, 2),
                "community_score": np.round(community, 3),
                "trust_rating": np.round(trust, 3),
                "repayment_history": np.round(repayment_history, 3),
                "financial_access_index": np.round(access, 3),
                "digital_access": np.round(digital_access, 3),
            }
        )

    df = pd.concat(
        [
            make_country("Malaysia", n_malaysia),
            make_country("Maldives", n_maldives),
        ],
        ignore_index=True,
    )
    return df