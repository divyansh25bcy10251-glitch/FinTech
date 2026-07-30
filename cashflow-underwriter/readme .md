# Cashflow Underwriter API 🚀

An end-to-end machine learning-powered cashflow underwriting and credit risk scoring API built with **FastAPI**, **XGBoost**, and **Pandas**. This service evaluates raw financial transaction histories, extracts key behavioral cashflow features, predicts default probabilities, and outputs automated lending decisions (Approved/Denied).

---

## 🛠️ Project Architecture & Files

* **`main.py`**: The core FastAPI application hosting the `/predict` endpoint and validation logic.
* **`train_model.py`**: Script used to train the XGBoost classifier on cashflow features.
* **`feature_engineering.py`**: Feature extraction pipeline calculating metrics like income frequency, discretionary spend ratios, and daily balances.
* **`generate_data.py`**: Generates synthetic cashflow datasets for model training and evaluation.
* **`plaid_service.py`**: Service handler for integration with financial data providers.
* **`test_api.py`**: Comprehensive `pytest` suite for automated API testing.
* **`xgb_model.pkl`**: Pre-trained XGBoost classification model.
* **`requirements.txt`**: Project dependency list.

---

## 📋 Extracted Cashflow Features
The model evaluates applicants based on core financial health indicators:
1. **`income_frequency`**: Number of distinct payroll/deposit inflows.
2. **`gig_income_total`**: Aggregate secondary or freelance income streams.
3. **`discretionary_spend_ratio`**: Proportion of non-essential retail/entertainment spending relative to total expenses.
4. **`utility_payments_count`**: Frequency of essential utility obligations met.
5. **`avg_daily_balance`**: Running net cash flow divided by transaction timeline length.

---
