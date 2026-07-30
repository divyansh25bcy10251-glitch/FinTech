"""Inference: raw transactions -> risk score + explanation."""

from __future__ import annotations

import os

import joblib
import numpy as np
import pandas as pd

from src.features import FEATURE_ORDER, compute_features

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
_BUNDLE = None


def _load():
    global _BUNDLE
    if _BUNDLE is None:
        path = os.path.join(MODEL_DIR, "risk_model.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Train the model first: python -m src.train")
        _BUNDLE = joblib.load(path)
    return _BUNDLE


def pd_to_score(pd_val: float, lo: int = 300, hi: int = 850) -> int:
    """Map probability-of-default to a FICO-like 300..850 score. Lower PD -> higher score."""
    return int(round(lo + (1.0 - pd_val) * (hi - lo)))


def risk_band(score: int) -> str:
    if score >= 750:
        return "Prime"
    if score >= 680:
        return "Near-Prime"
    if score >= 600:
        return "Subprime"
    return "Deep Subprime"


def score_transactions(tx_df: pd.DataFrame) -> dict:
    """
    Score a single borrower's transaction history.

    Parameters
    ----------
    tx_df : DataFrame with columns [date, amount, category, merchant, balance]
            All rows must belong to ONE borrower.
    """
    bundle = _load()
    model = bundle["model"]

    feats = compute_features(tx_df)
    x = pd.DataFrame([[feats[k] for k in FEATURE_ORDER]], columns=FEATURE_ORDER)
    pd_val = float(model.predict_proba(x)[0, 1])
    score = pd_to_score(pd_val, bundle["score_min"], bundle["score_max"])

    # simple explanation: top 5 features by SHAP-like contribution via LightGBM
    try:
        contribs = model.predict(x, pred_contrib=True)[0]
        # last element is bias
        feat_contrib = list(zip(FEATURE_ORDER, contribs[:-1]))
        top_pos = sorted(feat_contrib, key=lambda kv: kv[1], reverse=True)[:5]
        top_neg = sorted(feat_contrib, key=lambda kv: kv[1])[:5]
        explanation = {
            "raises_risk": [
                {"feature": n, "value": round(feats[n], 3), "impact": round(float(c), 4)}
                for n, c in top_pos if c > 0
            ],
            "lowers_risk": [
                {"feature": n, "value": round(feats[n], 3), "impact": round(float(c), 4)}
                for n, c in top_neg if c < 0
            ],
        }
    except Exception:
        explanation = {"raises_risk": [], "lowers_risk": []}

    return {
        "probability_of_default": round(pd_val, 4),
        "risk_score": score,
        "risk_band": risk_band(score),
        "features": {k: round(v, 4) for k, v in feats.items()},
        "explanation": explanation,
    }

if __name__ == "__main__":
    import pandas as pd

    # Load transaction data
    df = pd.read_csv("data/transactions.csv")

    # Get all transactions for borrower 1
    borrower_df = df[df["borrower_id"] == 1]

    # Predict
    result = score_transactions(borrower_df)

    print("\nPrediction Result")
    print("-----------------")
    print("\n===== Loan Risk Assessment =====")
print(f"Risk Score            : {result['risk_score']}")
print(f"Risk Band             : {result['risk_band']}")
print(f"Probability of Default: {result['probability_of_default']}")

print("\nFactors Increasing Risk:")
for item in result["explanation"]["raises_risk"]:
    print(f"- {item['feature']} ({item['value']})")

print("\nFactors Lowering Risk:")
for item in result["explanation"]["lowers_risk"]:
    print(f"- {item['feature']} ({item['value']})")
    