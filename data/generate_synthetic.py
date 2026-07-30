"""
Synthetic bank-transaction generator for the Cash-Flow Underwriting Engine.

Produces two CSVs:
  - transactions.csv : one row per transaction (borrower_id, date, amount, category, merchant)
  - labels.csv       : one row per borrower (borrower_id, defaulted)

Design goals
------------
* Model TWO borrower archetypes with a spectrum in between:
    - "Prime"    : stable salaried income, on-time rent/utilities, healthy buffer.
    - "Subprime" : irregular gig income, missed rent, overdrafts, high discretionary spend.
* Include GIG-ECONOMY payouts (Uber, DoorDash, Instacart) because that's the pitch.
* Default label is generated from a latent risk score + noise, so a model has real signal
  to learn but not a trivial leak.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

ESSENTIAL_CATS = ["rent", "utilities", "groceries", "insurance", "transport"]
DISCRETIONARY_CATS = ["dining", "entertainment", "shopping", "travel", "subscriptions"]
INCOME_CATS = ["salary", "gig_uber", "gig_doordash", "gig_instacart", "freelance"]

MERCHANTS = {
    "rent": ["LANDLORD ACH", "PROPERTY MGMT LLC"],
    "utilities": ["CITY POWER", "AQUA WATER", "COMCAST"],
    "groceries": ["WHOLEFOODS", "TRADER JOES", "KROGER"],
    "insurance": ["GEICO", "STATEFARM"],
    "transport": ["SHELL", "METRO CARD", "UBER RIDE"],
    "dining": ["STARBUCKS", "CHIPOTLE", "DOORDASH ORDER"],
    "entertainment": ["NETFLIX", "STEAM", "AMC THEATERS"],
    "shopping": ["AMAZON", "TARGET", "BESTBUY"],
    "travel": ["DELTA AIR", "AIRBNB", "MARRIOTT"],
    "subscriptions": ["SPOTIFY", "ICLOUD", "NYT"],
    "salary": ["ACME CORP PAYROLL"],
    "gig_uber": ["UBER PAYMENTS"],
    "gig_doordash": ["DOORDASH INC"],
    "gig_instacart": ["INSTACART PAY"],
    "freelance": ["UPWORK", "FIVERR"],
}


@dataclass
class BorrowerProfile:
    borrower_id: int
    archetype: str          # "prime" | "gig" | "subprime"
    monthly_income: float
    income_regularity: float  # 0..1 higher = more regular
    rent: float
    essential_ratio: float    # share of income spent on essentials
    discretionary_ratio: float
    starting_balance: float
    risk_latent: float        # 0..1 higher = more likely to default


def sample_profile(bid: int) -> BorrowerProfile:
    """Draw a borrower archetype with correlated parameters."""
    roll = RNG.random()
    if roll < 0.45:
        archetype = "prime"
        monthly_income = RNG.normal(6500, 1200)
        regularity = RNG.uniform(0.85, 1.0)
        rent = monthly_income * RNG.uniform(0.20, 0.30)
        essential = RNG.uniform(0.35, 0.50)
        discretionary = RNG.uniform(0.10, 0.20)
        starting = monthly_income * RNG.uniform(1.5, 3.5)
        latent = RNG.uniform(0.02, 0.15)
    elif roll < 0.80:
        archetype = "gig"
        monthly_income = RNG.normal(4200, 1500)
        regularity = RNG.uniform(0.40, 0.75)
        rent = monthly_income * RNG.uniform(0.28, 0.42)
        essential = RNG.uniform(0.45, 0.60)
        discretionary = RNG.uniform(0.15, 0.28)
        starting = monthly_income * RNG.uniform(0.4, 1.5)
        latent = RNG.uniform(0.15, 0.45)
    else:
        archetype = "subprime"
        monthly_income = RNG.normal(2800, 900)
        regularity = RNG.uniform(0.15, 0.45)
        rent = monthly_income * RNG.uniform(0.35, 0.55)
        essential = RNG.uniform(0.50, 0.70)
        discretionary = RNG.uniform(0.20, 0.40)
        starting = monthly_income * RNG.uniform(0.0, 0.8)
        latent = RNG.uniform(0.40, 0.85)

    monthly_income = max(1200.0, monthly_income)
    return BorrowerProfile(
        borrower_id=bid,
        archetype=archetype,
        monthly_income=float(monthly_income),
        income_regularity=float(regularity),
        rent=float(rent),
        essential_ratio=float(essential),
        discretionary_ratio=float(discretionary),
        starting_balance=float(starting),
        risk_latent=float(latent),
    )


def _income_dates(start: date, end: date, regularity: float, archetype: str) -> list[date]:
    """Return the dates income lands. Prime = biweekly; gig = many small irregular."""
    dates = []
    if archetype == "prime":
        d = start + timedelta(days=int(RNG.integers(0, 14)))
        while d <= end:
            jitter = int(RNG.integers(-1, 2)) if regularity < 0.95 else 0
            dates.append(d + timedelta(days=jitter))
            d += timedelta(days=14)
    else:
        # gig / subprime: many small deposits, cadence varies with regularity
        d = start
        mean_gap = 2 if archetype == "gig" else 4
        while d <= end:
            gap = max(1, int(RNG.exponential(mean_gap / max(regularity, 0.1))))
            d += timedelta(days=gap)
            if d <= end:
                dates.append(d)
    return dates


def _income_amounts(p: BorrowerProfile, n_events: int) -> np.ndarray:
    """Split monthly income across n events with noise scaled by (1 - regularity)."""
    months = max(1, n_events * 14 / 30) if p.archetype == "prime" else max(1, n_events / 8)
    total = p.monthly_income * months
    base = np.full(n_events, total / n_events)
    noise = RNG.normal(0, (1 - p.income_regularity) * base.mean() * 0.6, n_events)
    return np.clip(base + noise, 20, None)


def generate_borrower(p: BorrowerProfile, start: date, end: date) -> pd.DataFrame:
    rows: list[dict] = []
    balance = p.starting_balance

    # -------- income --------
    inc_dates = _income_dates(start, end, p.income_regularity, p.archetype)
    if not inc_dates:
        inc_dates = [start + timedelta(days=15)]
    inc_amts = _income_amounts(p, len(inc_dates))

    for d, amt in zip(inc_dates, inc_amts):
        if p.archetype == "prime":
            cat = "salary"
        else:
            cat = RNG.choice(
                ["gig_uber", "gig_doordash", "gig_instacart", "freelance", "salary"],
                p=[0.35, 0.25, 0.15, 0.15, 0.10],
            )
        merchant = RNG.choice(MERCHANTS[cat])
        balance += amt
        rows.append(dict(borrower_id=p.borrower_id, date=d, amount=round(float(amt), 2),
                         category=cat, merchant=str(merchant), balance=round(balance, 2)))

    # -------- rent (monthly, sometimes missed for high-risk borrowers) --------
    d = date(start.year, start.month, min(28, start.day))
    while d <= end:
        miss_prob = 0.02 + p.risk_latent * 0.35
        if RNG.random() > miss_prob:
            balance -= p.rent
            rows.append(dict(borrower_id=p.borrower_id, date=d, amount=-round(p.rent, 2),
                             category="rent", merchant=str(RNG.choice(MERCHANTS["rent"])),
                             balance=round(balance, 2)))
        # advance one month
        year = d.year + (d.month // 12)
        month = (d.month % 12) + 1
        d = date(year, month, min(28, d.day))

    # -------- utilities (monthly) --------
    d = start + timedelta(days=int(RNG.integers(3, 10)))
    while d <= end:
        for cat in ["utilities", "insurance"]:
            amt = p.monthly_income * RNG.uniform(0.02, 0.06)
            balance -= amt
            rows.append(dict(borrower_id=p.borrower_id, date=d, amount=-round(amt, 2),
                             category=cat, merchant=str(RNG.choice(MERCHANTS[cat])),
                             balance=round(balance, 2)))
        d += timedelta(days=30)

    # -------- daily discretionary + groceries --------
    n_days = (end - start).days
    essential_budget = p.monthly_income * p.essential_ratio
    disc_budget = p.monthly_income * p.discretionary_ratio
    daily_ess = essential_budget / 30
    daily_disc = disc_budget / 30

    for i in range(n_days):
        d = start + timedelta(days=i)
        # essentials (groceries, transport)
        if RNG.random() < 0.55:
            cat = RNG.choice(["groceries", "transport"])
            amt = max(3, RNG.normal(daily_ess * 1.2, daily_ess * 0.5))
            balance -= amt
            rows.append(dict(borrower_id=p.borrower_id, date=d, amount=-round(amt, 2),
                             category=cat, merchant=str(RNG.choice(MERCHANTS[cat])),
                             balance=round(balance, 2)))
        # discretionary — higher for subprime
        disc_freq = 0.35 + p.discretionary_ratio
        if RNG.random() < disc_freq:
            cat = RNG.choice(DISCRETIONARY_CATS)
            amt = max(2, RNG.normal(daily_disc * 1.3, daily_disc * 0.7))
            balance -= amt
            rows.append(dict(borrower_id=p.borrower_id, date=d, amount=-round(amt, 2),
                             category=cat, merchant=str(RNG.choice(MERCHANTS[cat])),
                             balance=round(balance, 2)))

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    # recompute running balance so it stays consistent after sort
    df["balance"] = (p.starting_balance + df["amount"].cumsum()).round(2)
    return df


def default_label(p: BorrowerProfile, df: pd.DataFrame) -> int:
    """Turn latent risk + observed behaviour into a 0/1 default label."""
    overdrafts = int((df["balance"] < 0).sum())
    missed_rent_penalty = 0
    rent_events = df[df["category"] == "rent"]
    months = max(1, ((df["date"].max() - df["date"].min()).days // 30))
    if len(rent_events) < months - 1:
        missed_rent_penalty = 0.15 * (months - len(rent_events))

    score = (
        p.risk_latent
        + min(overdrafts / 20, 0.25)
        + min(missed_rent_penalty, 0.35)
        - (0.15 if p.archetype == "prime" else 0.0)
    )
    prob = 1 / (1 + np.exp(-6 * (score - 0.45)))  # sigmoid
    return int(RNG.random() < prob)


def main(n_borrowers: int, out_dir: str) -> None:
    end = date(2026, 6, 30)
    start = end - timedelta(days=180)  # 6 months of history

    all_tx: list[pd.DataFrame] = []
    labels: list[dict] = []

    for bid in range(1, n_borrowers + 1):
        p = sample_profile(bid)
        df = generate_borrower(p, start, end)
        all_tx.append(df)
        labels.append(dict(
            borrower_id=bid,
            archetype=p.archetype,
            defaulted=default_label(p, df),
        ))
        if bid % 500 == 0:
            print(f"  generated {bid}/{n_borrowers}")

    tx_df = pd.concat(all_tx, ignore_index=True)
    labels_df = pd.DataFrame(labels)

    os.makedirs(out_dir, exist_ok=True)
    tx_path = os.path.join(out_dir, "transactions.csv")
    lb_path = os.path.join(out_dir, "labels.csv")
    tx_df.to_csv(tx_path, index=False)
    labels_df.to_csv(lb_path, index=False)

    print(f"\nWrote {len(tx_df):,} transactions across {n_borrowers} borrowers")
    print(f"  -> {tx_path}")
    print(f"  -> {lb_path}")
    print(f"Default rate: {labels_df['defaulted'].mean():.1%}")
    print(f"By archetype:\n{labels_df.groupby('archetype')['defaulted'].mean().round(3)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000, help="number of borrowers")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    main(args.n, args.out)
