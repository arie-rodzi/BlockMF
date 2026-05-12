import hashlib
from datetime import datetime, timezone
import pandas as pd


def create_transaction(borrower_id: str, decision: str, amount: float, score: float, country: str) -> dict:
    """Create blockchain-style transaction record using hash simulation."""
    timestamp = datetime.now(timezone.utc).isoformat()
    raw = f"{borrower_id}|{decision}|{amount}|{score}|{country}|{timestamp}"
    tx_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    return {
        "timestamp": timestamp,
        "borrower_id": borrower_id,
        "country": country,
        "decision": decision,
        "amount": round(float(amount), 2),
        "eligibility_score": round(float(score), 4),
        "transaction_hash": "0x" + tx_hash[:40],
        "verification_status": "Verified",
    }


def generate_ledger(scored_df: pd.DataFrame, max_records: int = 80) -> pd.DataFrame:
    """Generate ledger records for approved/review/conditional borrowers."""
    eligible = scored_df[scored_df["decision"].isin(["Approved", "Review", "Conditional"])].head(max_records)

    records = [
        create_transaction(
            borrower_id=row["borrower_id"],
            decision=row["decision"],
            amount=row["loan_amount"],
            score=row["eligibility_score"],
            country=row["country"],
        )
        for _, row in eligible.iterrows()
    ]

    return pd.DataFrame(records)