import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_empty_transactions():
    response = client.post("/predict", json={"transactions": []})
    assert response.status_code == 400

def test_prime_saver_profile():
    payload = {
      "transactions": [
        {"date": "2026-06-01", "amount": 10000.0, "name": "Salary", "category": "payroll"},
        {"date": "2026-06-03", "amount": -1800.0, "name": "Rent", "category": "rent"},
        {"date": "2026-06-12", "amount": -110.0, "name": "Electric", "category": "utility"}
      ]
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "Approved"
    assert data["risk_tier"] == "Low Risk"

def test_zero_income_profile():
    payload = {
      "transactions": [
        {"date": "2026-06-03", "amount": -1500.0, "name": "Unknown Debt", "category": "general"}
      ]
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "Denied"
    assert data["risk_tier"] == "High Risk"