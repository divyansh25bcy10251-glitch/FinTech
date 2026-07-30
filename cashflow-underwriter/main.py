from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import xgboost as xgb
import joblib
import os

app = FastAPI(title="Cashflow Underwriter API")

class TransactionItem(BaseModel):
    date: str
    amount: float
    name: Optional[str] = "Unknown"
    category: Optional[str] = "General"

class ApplicationPayload(BaseModel):
    transactions: List[TransactionItem]

class PredictionResponse(BaseModel):
    credit_score: int
    default_probability: float
    risk_tier: str
    decision: str
    extracted_features: dict

# Load your trained XGBoost model
model = xgb.XGBClassifier()
MODEL_PATH = "xgb_model.pkl"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

@app.post("/predict", response_model=PredictionResponse)
def predict_credit(payload: ApplicationPayload):
    # Explicit check to catch empty lists and return a 400 Bad Request
    if not payload.transactions:
        raise HTTPException(status_code=400, detail="Transactions list cannot be empty.")

    try:
        tx_data = [dict(tx) for tx in payload.transactions]
        df = pd.DataFrame(tx_data)
        
        # Fixed logic: Positive amounts are deposits/income, negative amounts are spends/withdrawals
        deposits_df = df[df['amount'] > 0].copy()
        spend_df = df[df['amount'] < 0].copy()

        total_spend = abs(float(spend_df['amount'].sum())) if not spend_df.empty else 0.0
        total_deposits = float(deposits_df['amount'].sum()) if not deposits_df.empty else 0.0
        net_flow = total_deposits - total_spend
        
        income_frequency = int(len(deposits_df))
        gig_income_total = 0.0

        def check_cat(cat):
            return 'rent' in str(cat).lower() or 'utility' in str(cat).lower() or 'grocery' in str(cat).lower()

        is_essential = spend_df['category'].apply(check_cat) if 'category' in spend_df.columns else pd.Series([False]*len(spend_df))
        essential_spend = abs(float(spend_df[is_essential]['amount'].sum())) if not spend_df.empty else 0.0
        
        discretionary_spend = total_spend - essential_spend
        discretionary_spend_ratio = float(discretionary_spend / total_spend) if total_spend > 0 else 0.0

        utility_payments_count = int(spend_df['category'].apply(lambda c: 'utility' in str(c).lower()).sum()) if not spend_df.empty else 0
        avg_daily_balance = float(net_flow / max(len(df.groupby('date')), 1))

        features_dict = {
            "income_frequency": income_frequency,
            "gig_income_total": gig_income_total,
            "discretionary_spend_ratio": discretionary_spend_ratio,
            "utility_payments_count": utility_payments_count,
            "avg_daily_balance": avg_daily_balance
        }

        features_df = pd.DataFrame([features_dict])

        if model is not None:
            probabilities = model.predict_proba(features_df)
            default_probability = float(probabilities[0][1])
        else:
            default_probability = min(max(discretionary_spend_ratio * 0.5 + (0.1 if income_frequency < 2 else 0.0), 0.01), 0.99)

        credit_score = int(round((1.0 - default_probability) * 850))
        risk_tier = "Low Risk" if default_probability < 0.7 else "High Risk"
        decision = "Approved" if risk_tier == "Low Risk" else "Denied"

        return {
            "credit_score": credit_score,
            "default_probability": round(default_probability, 4),
            "risk_tier": risk_tier,
            "decision": decision,
            "extracted_features": features_dict
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))