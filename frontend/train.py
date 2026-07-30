"""
Train the LightGBM default-risk model on the engineered cash-flow features.

Outputs:
  models/risk_model.pkl   : trained model + feature order + calibration bounds
  models/metrics.json     : AUC, KS, precision/recall @ 0.5, feature importances
"""

from __future__ import annotations

import json
import os
import sys

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from src.features import FEATURE_ORDER, build_feature_matrix  # noqa: E402

DATA_DIR = os.path.join(ROOT, "data")
MODEL_DIR = os.path.join(ROOT, "models")


def ks_statistic(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Kolmogorov-Smirnov — standard credit-risk separation metric."""
    order = np.argsort(y_prob)[::-1]
    y_true = np.asarray(y_true)[order]
    cum_pos = np.cumsum(y_true) / max(y_true.sum(), 1)
    cum_neg = np.cumsum(1 - y_true) / max((1 - y_true).sum(), 1)
    return float(np.max(np.abs(cum_pos - cum_neg)))


def main() -> None:
    tx_path = os.path.join(DATA_DIR, "transactions.csv")
    lb_path = os.path.join(DATA_DIR, "labels.csv")
    if not (os.path.exists(tx_path) and os.path.exists(lb_path)):
        raise SystemExit(
            f"Missing data. Run: python {os.path.join(DATA_DIR, 'generate_synthetic.py')}"
        )

    print("Loading data...")
    tx = pd.read_csv(tx_path)
    labels = pd.read_csv(lb_path).set_index("borrower_id")

    print(f"  {len(tx):,} txns / {len(labels):,} borrowers "
          f"(default rate {labels['defaulted'].mean():.1%})")

    print("Engineering features...")
    X = build_feature_matrix(tx)
    X = X.reindex(columns=FEATURE_ORDER)
    y = labels.loc[X.index, "defaulted"].astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    print(f"Training LightGBM on {len(X_train)} borrowers...")
    model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.03,
        num_leaves=31,
        min_child_samples=20,
        reg_alpha=0.1,
        reg_lambda=0.1,
        objective="binary",
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[lgb.early_stopping(30, verbose=False)],
    )

    prob_test = model.predict_proba(X_test)[:, 1]
    pred_test = (prob_test >= 0.5).astype(int)

    auc = roc_auc_score(y_test, prob_test)
    ap = average_precision_score(y_test, prob_test)
    ks = ks_statistic(y_test, prob_test)
    cm = confusion_matrix(y_test, pred_test).tolist()
    report = classification_report(y_test, pred_test, output_dict=True, zero_division=0)

    print(f"\n=== Test metrics ===")
    print(f"  ROC-AUC        : {auc:.4f}")
    print(f"  Avg Precision  : {ap:.4f}")
    print(f"  KS statistic   : {ks:.4f}")
    print(f"  Confusion matrix (rows=true, cols=pred):")
    print(f"    non-default  : {cm[0]}")
    print(f"    default      : {cm[1]}")

    importances = sorted(
        zip(FEATURE_ORDER, model.feature_importances_),
        key=lambda kv: kv[1],
        reverse=True,
    )
    print(f"\n  Top-10 features:")
    for name, imp in importances[:10]:
        print(f"    {name:<24} {int(imp)}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    bundle = {
        "model": model,
        "feature_order": FEATURE_ORDER,
        # calibration bounds for translating PD → 300–850 score (FICO-like)
        "score_min": 300,
        "score_max": 850,
    }
    model_path = os.path.join(MODEL_DIR, "risk_model.pkl")
    joblib.dump(bundle, model_path)

    metrics = {
        "roc_auc": auc,
        "average_precision": ap,
        "ks_statistic": ks,
        "confusion_matrix": cm,
        "classification_report": report,
        "feature_importances": [{"feature": n, "importance": int(i)} for n, i in importances],
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }
    metrics_path = os.path.join(MODEL_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nSaved model  -> {model_path}")
    print(f"Saved metrics-> {metrics_path}")


if __name__ == "__main__":
    main()
