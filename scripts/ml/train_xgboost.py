"""
Train XGBoost Model
"""

from __future__ import annotations

import json

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from config import (
    FINAL_DATASET,
    RANDOM_STATE,
    TEST_SIZE,
    XGBOOST_MODEL,
    XGBOOST_REPORT,
    FEATURE_IMPORTANCE,
)

print("=" * 60)
print("Loading Dataset")
print("=" * 60)

df = pd.read_csv(FINAL_DATASET)

X = df.drop(columns=["risk_level"])
y = df["risk_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y,
)

print("Training XGBoost...")

model = XGBClassifier(
    objective="multi:softmax",
    num_class=3,
    n_estimators=250,
    max_depth=6,
    learning_rate=0.05,
    random_state=RANDOM_STATE,
)

model.fit(X_train, y_train)

prediction = model.predict(X_test)

accuracy = accuracy_score(y_test, prediction)
precision = precision_score(y_test, prediction, average="weighted")
recall = recall_score(y_test, prediction, average="weighted")
f1 = f1_score(y_test, prediction, average="weighted")

print()
print("=" * 60)
print("XGBoost Performance")
print("=" * 60)

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")

print()
print(classification_report(y_test, prediction))
print()
print(confusion_matrix(y_test, prediction))

joblib.dump(model, XGBOOST_MODEL)

importance = pd.DataFrame(
    {
        "Feature": X.columns,
        "Importance": model.feature_importances_,
    }
)

importance.sort_values(
    by="Importance",
    ascending=False,
    inplace=True,
)

importance.to_csv(
    FEATURE_IMPORTANCE.with_name("xgboost_feature_importance.csv"),
    index=False,
)

metrics = {
    "model": "XGBoost",
    "accuracy": float(accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
}

with open(XGBOOST_REPORT, "w") as file:
    json.dump(metrics, file, indent=4)

print()
print("Model Saved Successfully")