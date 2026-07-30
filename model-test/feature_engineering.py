import pandas as pd

def extract_features(transactions_response: dict) -> dict:
    """
    Parses Plaid transaction JSON and extracts cash-flow variables.
    """
    raw_txns = transactions_response.get("transactions", [])
    
    if not raw_txns:
        return {
            "income_frequency": 0,
            "gig_income_total": 0.0,
            "discretionary_spend_ratio": 0.0,
            "utility_payments_count": 0,
            "avg_daily_balance": 0.0
        }

    df = pd.DataFrame(raw_txns)
    
    # 1. Income Frequency & Gig Payouts
    deposits_df = df[df['amount'] < 0].copy()
    income_frequency = len(deposits_df)
    
    gig_keywords = 'uber|doordash|lyft|swiggy|zomato|blinkit|instacart'
    is_gig = deposits_df['name'].str.contains(gig_keywords, case=False, na=False)
    gig_income_total = abs(deposits_df[is_gig]['amount'].sum())

    # 2. Spend Ratios (Essential vs Discretionary)
    spend_df = df[df['amount'] > 0].copy()
    total_spend = spend_df['amount'].sum()

    def check_category(cats, keywords):
        if not isinstance(cats, list):
            return False
        return any(any(k.lower() in c.lower() for k in keywords) for c in cats)

    essential_keywords = ['rent', 'utility', 'groceries', 'supermarket', 'payment']
    is_essential = spend_df['category'].apply(lambda x: check_category(x, essential_keywords))
    
    essential_spend = spend_df[is_essential]['amount'].sum()
    discretionary_spend_ratio = float(essential_spend / total_spend) if total_spend > 0 else 0.0

    # 3. Utility / Rent Regularity count
    utility_keywords = ['electric', 'water', 'gas', 'rent', 'internet', 'telecom']
    is_utility = df['name'].str.contains('|'.join(utility_keywords), case=False, na=False)
    utility_payments_count = int(df[is_utility & (df['amount'] > 0)].shape[0])

    # 4. Average Daily Balance Proxy
    net_flow = abs(deposits_df['amount'].sum()) - total_spend
    avg_daily_balance = float(max(0.0, net_flow / 3.0))

    return {
        "income_frequency": int(income_frequency),
        "gig_income_total": float(gig_income_total),
        "discretionary_spend_ratio": float(discretionary_spend_ratio),
        "utility_payments_count": int(utility_payments_count),
        "avg_daily_balance": float(avg_daily_balance)
    }