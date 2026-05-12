import hashlib
import pandas as pd
from datetime import datetime, timezone


def make_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_ledger(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    prev_hash = "GENESIS"
    approved = df[df["decision"].isin(["Approved", "Review"])].head(120).copy()

    for i, row in approved.iterrows():
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = f"{prev_hash}|{row['borrower_id']}|{row['requested_loan']}|{row['eligibility_score']:.4f}|{row['decision']}|{timestamp}"
        tx_hash = make_hash(payload)
        records.append({
            "block_no": len(records) + 1,
            "timestamp": timestamp,
            "borrower_id": row["borrower_id"],
            "country": row["country"],
            "amount": row["requested_loan"],
            "decision": row["decision"],
            "eligibility_score": round(row["eligibility_score"], 4),
            "previous_hash": prev_hash[:16] + "..." if prev_hash != "GENESIS" else prev_hash,
            "transaction_hash": tx_hash[:24] + "...",
        })
        prev_hash = tx_hash
    return pd.DataFrame(records)
