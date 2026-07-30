import numpy as np
import pandas as pd

def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)
    
    income_frequency = np.random.randint(2, 30, num_samples)
    gig_income_total = np.random.exponential(scale=500.0, size=num_samples)
    discretionary_spend_ratio = np.random.uniform(0.1, 0.9, num_samples)
    utility_payments_count = np.random.randint(0, 6, num_samples)
    avg_daily_balance = np.random.normal(loc=1500, scale=800, size=num_samples)
    avg_daily_balance = np.clip(avg_daily_balance, 50, 10000)

    risk_score = (
        (500 - avg_daily_balance / 20) + 
        (discretionary_spend_ratio * 300) - 
        (income_frequency * 5) - 
        (utility_payments_count * 20)
    )
    
    risk_score += np.random.normal(0, 50, num_samples)
    defaulted = (risk_score > np.median(risk_score)).astype(int)

    df = pd.DataFrame({
        "income_frequency": income_frequency,
        "gig_income_total": gig_income_total,
        "discretionary_spend_ratio": discretionary_spend_ratio,
        "utility_payments_count": utility_payments_count,
        "avg_daily_balance": avg_daily_balance,
        "defaulted": defaulted
    })

    df.to_csv("synthetic_cashflow_data.csv", index=False)
    print("Synthetic dataset 'synthetic_cashflow_data.csv' created successfully!")

if __name__ == "__main__":
    generate_synthetic_data()