"""
Cash-flow feature engineering.

Takes a per-borrower transaction dataframe and emits a single-row feature vector
that a downstream model (LightGBM) consumes. All features are designed to be
computable from raw bank-transaction data — the whole point of the pitch.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

INCOME_CATS = ["salary", "gig_uber", "gig_doordash", "gig_instacart", "freelance"]
GIG_CATS = ["gig_uber", "gig_doordash", "gig_instacart"]
ESSENTIAL_CATS = ["rent", "utilities", "groceries", "insurance", "transport"]
DISCRETIONARY_CATS = ["dining", "entertainment", "shopping", "travel", "subscriptions"]


def _safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b else 0.0


def compute_features(df: pd.DataFrame) -> dict[str, float]:
    """Return one feature dict for a single borrower's transaction history."""
    if df.empty:
        raise ValueError("empty transaction frame")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    total_days = max(1, (df["date"].max() - df["date"].min()).days)
    months = total_days / 30.0

    income = df[df["category"].isin(INCOME_CATS)]
    expense = df[~df["category"].isin(INCOME_CATS)]
    gig = df[df["category"].isin(GIG_CATS)]
    ess = df[df["category"].isin(ESSENTIAL_CATS)]
    disc = df[df["category"].isin(DISCRETIONARY_CATS)]
    rent = df[df["category"] == "rent"]

    total_income = float(income["amount"].sum())
    total_expense = float(-expense["amount"].sum())
    monthly_income = _safe_div(total_income, months)
    monthly_expense = _safe_div(total_expense, months)

    # income regularity: coefficient of variation of gaps between income events
    if len(income) >= 3:
        gaps = np.diff(income["date"].values).astype("timedelta64[D]").astype(int)
        income_gap_mean = float(gaps.mean())
        income_gap_cv = float(gaps.std() / gaps.mean()) if gaps.mean() else 0.0
    else:
        income_gap_mean = float(total_days)
        income_gap_cv = 1.0

    # rent regularity: how many of the expected months had a rent event
    expected_rent_months = max(1, int(round(months)))
    rent_paid_months = rent["date"].dt.to_period("M").nunique()
    rent_on_time_ratio = _safe_div(rent_paid_months, expected_rent_months)

    # balance stability
    bal = df["balance"].values
    avg_balance = float(bal.mean())
    min_balance = float(bal.min())
    balance_volatility = float(bal.std())
    days_negative = int((bal < 0).sum())
    overdraft_events = int(((bal < 0) & (np.r_[True, bal[:-1] >= 0])).sum())

    # income mix
    gig_income = float(gig["amount"].sum())
    salary_income = float(df[df["category"] == "salary"]["amount"].sum())
    gig_share = _safe_div(gig_income, total_income)

    # spend mix
    essential_spend = float(-ess["amount"].sum())
    discretionary_spend = float(-disc["amount"].sum())
    disc_to_ess_ratio = _safe_div(discretionary_spend, essential_spend)

    # weekend spend
    df["dow"] = df["date"].dt.dayofweek
    weekend_spend = float(-df[(df["dow"] >= 5) & (df["amount"] < 0)]["amount"].sum())
    weekend_spend_ratio = _safe_div(weekend_spend, total_expense)

    # income trend: slope of monthly income (last 3 vs first 3 months)
    df["ym"] = df["date"].dt.to_period("M")
    monthly = df[df["category"].isin(INCOME_CATS)].groupby("ym")["amount"].sum().sort_index()
    if len(monthly) >= 4:
        early = monthly.iloc[: len(monthly) // 2].mean()
        late = monthly.iloc[len(monthly) // 2 :].mean()
        income_trend = _safe_div(late - early, abs(early)) if early else 0.0
    else:
        income_trend = 0.0

    # cash-flow ratio (net savings)
    net_cashflow = total_income - total_expense
    savings_rate = _safe_div(net_cashflow, total_income)

    # transaction velocity
    txn_per_day = _safe_div(len(df), total_days)
    unique_merchants = int(df["merchant"].nunique())

    # income-to-rent ratio (housing burden)
    monthly_rent = _safe_div(float(-rent["amount"].sum()), months)
    rent_to_income = _safe_div(monthly_rent, monthly_income)

    # income concentration (are we living paycheck to paycheck?)
    largest_income = float(income["amount"].max()) if not income.empty else 0.0
    income_concentration = _safe_div(largest_income, total_income)

    return {
        "total_days": float(total_days),
        "n_transactions": float(len(df)),
        "txn_per_day": txn_per_day,
        "unique_merchants": float(unique_merchants),

        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "net_cashflow": net_cashflow,
        "savings_rate": savings_rate,

        "income_gap_mean": income_gap_mean,
        "income_gap_cv": income_gap_cv,
        "income_trend": income_trend,
        "income_concentration": income_concentration,

        "gig_share": gig_share,
        "gig_income": gig_income,
        "salary_income": salary_income,

        "essential_spend": essential_spend,
        "discretionary_spend": discretionary_spend,
        "disc_to_ess_ratio": disc_to_ess_ratio,
        "weekend_spend_ratio": weekend_spend_ratio,

        "rent_on_time_ratio": rent_on_time_ratio,
        "rent_to_income": rent_to_income,

        "avg_balance": avg_balance,
        "min_balance": min_balance,
        "balance_volatility": balance_volatility,
        "days_negative": float(days_negative),
        "overdraft_events": float(overdraft_events),
    }


def build_feature_matrix(tx_df: pd.DataFrame) -> pd.DataFrame:
    """Compute features for every borrower_id in tx_df."""
    rows = []
    for bid, sub in tx_df.groupby("borrower_id"):
        feats = compute_features(sub)
        feats["borrower_id"] = bid
        rows.append(feats)
    out = pd.DataFrame(rows).set_index("borrower_id").sort_index()
    return out


FEATURE_ORDER = [
    "total_days", "n_transactions", "txn_per_day", "unique_merchants",
    "monthly_income", "monthly_expense", "net_cashflow", "savings_rate",
    "income_gap_mean", "income_gap_cv", "income_trend", "income_concentration",
    "gig_share", "gig_income", "salary_income",
    "essential_spend", "discretionary_spend", "disc_to_ess_ratio", "weekend_spend_ratio",
    "rent_on_time_ratio", "rent_to_income",
    "avg_balance", "min_balance", "balance_volatility",
    "days_negative", "overdraft_events",
]
