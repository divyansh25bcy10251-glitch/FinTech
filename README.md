# CashFlowAI – AI-Powered Cash-Flow Underwriting Engine

## Overview

**CashFlowAI** is an AI-powered loan risk assessment system that evaluates an individual's financial behavior using their bank transaction history instead of relying only on traditional credit scores.

Many freelancers, gig workers, students, and first-time borrowers have little or no credit history, making it difficult for them to access loans. CashFlowAI addresses this problem by analyzing real cash flow patterns such as income consistency, spending habits, bill payments, and account balances to generate a fairer and more accurate credit risk score.

---

## Problem Statement

Traditional lending systems mainly depend on credit scores to determine whether someone qualifies for a loan.

This creates challenges because:

* Many young adults have no credit history.
* Freelancers and gig workers often receive irregular income.
* Responsible financial behavior is not reflected in a credit score.
* Deserving borrowers may be rejected despite having healthy financial habits.

---

## Our Solution

CashFlowAI uses Artificial Intelligence and Machine Learning to analyze a customer's financial behavior directly from their transaction history.

Instead of asking:

> **"What is your credit score?"**

Our system asks:

> **"How responsibly do you manage your money?"**

The model studies transaction patterns and predicts the probability that a borrower will successfully repay a loan.

---

## Objectives

* Improve financial inclusion for individuals with limited credit history.
* Provide a more accurate loan risk assessment.
* Reduce default rates for lenders.
* Support fair lending decisions using real financial behavior.

---

## Features

* Cash Flow Analysis
* Income Frequency Detection
* Rent Payment Tracking
* Utility Bill Payment Analysis
* Daily Average Balance Monitoring
* Spending Habit Classification
* Loan Default Risk Prediction
* AI-Based Credit Risk Scoring
* Secure Bank Data Integration (via Open Banking APIs)

---

## Key Financial Indicators

The model evaluates:

* Income consistency
* Salary frequency
* Gig economy earnings (Uber, DoorDash, Swiggy, Zomato, etc.)
* Rent payment regularity
* Utility bill payments
* Daily average account balance
* Savings trends
* Essential vs discretionary spending ratio
* Cash flow stability

---

## Machine Learning Model

The project uses Gradient Boosting algorithms because they perform exceptionally well on structured financial data.

Recommended models:

* LightGBM
* XGBoost

The model predicts:

* Probability of loan repayment
* Probability of loan default
* Overall borrower risk score

---

## System Workflow

```text
User Applies for Loan
          │
          ▼
Connect Bank Account
          │
          ▼
Fetch Transaction History
          │
          ▼
Extract Financial Features
          │
          ▼
AI/ML Risk Prediction
          │
          ▼
Generate Risk Score
          │
          ▼
Approve / Reject Loan
```

---

## Tech Stack

### Programming Language

* Python
*javascript
*CSS
*HTML

### Machine Learning

* LightGBM
* XGBoost
* Scikit-learn

### Data Processing

* Pandas
* NumPy

### APIs


### Backend

* Flask / FastAPI

### Frontend

* React.js
* HTML
* CSS
* JavaScript

### Database

* PostgreSQL
* MongoDB

### Visualization

* Matplotlib
* Plotly

---

## Example Risk Analysis

### Input

* Monthly Income: ₹45,000
* Rent Paid: On Time
* Utility Bills: Paid Regularly
* Stable Average Balance
* Controlled Spending
* Regular Freelance Payments

### Output

```text
Risk Score: 92%

Loan Recommendation:
✅ APPROVED
```

---

## Real-World Applications

* Digital Lending Platforms
* FinTech Startups
* Banks
* Credit Unions
* Buy Now Pay Later (BNPL) Services
* Microfinance Institutions

---

## Future Enhancements

* Explainable AI (XAI) for transparent lending decisions
* Fraud detection using anomaly detection
* Personalized financial health insights
* Loan repayment recommendations
* Real-time transaction monitoring
* Mobile application support
* Alternative financial data integration

---

## Benefits

### For Borrowers

* Fair loan evaluation
* Better access to credit
* No dependence solely on credit scores

### For Lenders

* Improved risk prediction
* Lower default rates
* Faster loan approval process
* More informed lending decisions

---

## Privacy & Security

Customer financial data is handled securely using encrypted connections and permission-based access through Open Banking APIs. Users remain in control of their financial information, and no data is accessed without explicit consent.

---

## Project Status

Hackathon Prototype

This project demonstrates the concept of AI-driven cash-flow underwriting and can be further developed into a production-ready financial risk assessment platform.

---

## Team

Divyansh shrivastava  
Manya Goyal  
Rashi Agarwal  
Ananya Kesherwani  
Pranav

---

## License

This project is intended for educational and research purposes.

---

## Why CashFlowAI?

Traditional credit scoring looks at the past.

**CashFlowAI looks at the present financial behavior.**

By analyzing real cash flow instead of only credit history, the platform enables smarter, fairer, and more inclusive lending decisions powered by Artificial Intelligence.
