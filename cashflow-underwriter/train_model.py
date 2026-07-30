import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle

def train():
    df = pd.read_csv('synthetic_cashflow_data.csv')
    
    X = df[['income_frequency', 'gig_income_total', 'discretionary_spend_ratio', 'utility_payments_count', 'avg_daily_balance']]
    y = df['defaulted']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        max_depth=4,
        learning_rate=0.05,
        n_estimators=100
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(f"Model Accuracy: {accuracy_score(y_test, preds) * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, preds))

    with open('xgb_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("\nModel successfully saved to xgb_model.pkl!")

if __name__ == "__main__":
    train()