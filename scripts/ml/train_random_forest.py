"""
Random Forest Training Script

This script trains the Random Forest classifier,
evaluates it and saves the trained model.
"""

from __future__ import annotations

import json

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from config import (
    FEATURE_COLUMNS,
    FEATURE_IMPORTANCE,
    FINAL_DATASET,
    RANDOM_FOREST_MODEL,
    RANDOM_FOREST_REPORT,
    RANDOM_STATE,
    TEST_SIZE,
)

print("=" * 60)
print("Loading Dataset")
print("=" * 60)

df = pd.read_csv(FINAL_DATASET)

print(df.head())

print()

print(f"Total Records : {len(df)}")

# --------------------------------------------------------
# Features
# --------------------------------------------------------

X = df.drop(columns=["risk_level"])

y = df["risk_level"]

# --------------------------------------------------------
# Train Test Split
# --------------------------------------------------------

print()

print("Splitting Dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y,
)

print(f"Training Records : {len(X_train)}")
print(f"Testing Records  : {len(X_test)}")

# --------------------------------------------------------
# Model
# --------------------------------------------------------

print()

print("Training Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    random_state=RANDOM_STATE,
)

model.fit(X_train, y_train)

print("Training Completed.")

# --------------------------------------------------------
# Prediction
# --------------------------------------------------------

prediction = model.predict(X_test)

# --------------------------------------------------------
# Metrics
# --------------------------------------------------------

accuracy = accuracy_score(y_test, prediction)

precision = precision_score(
    y_test,
    prediction,
    average="weighted",
)

recall = recall_score(
    y_test,
    prediction,
    average="weighted",
)

f1 = f1_score(
    y_test,
    prediction,
    average="weighted",
)

print()

print("=" * 60)
print("Random Forest Performance")
print("=" * 60)

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print()

print(classification_report(y_test, prediction))

print()

print(confusion_matrix(y_test, prediction))

# --------------------------------------------------------
# Save Model
# --------------------------------------------------------

joblib.dump(model, RANDOM_FOREST_MODEL)

print()

print("Model Saved.")

# --------------------------------------------------------
# Save Feature Importance
# --------------------------------------------------------

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
    FEATURE_IMPORTANCE,
    index=False,
)

print("Feature Importance Saved.")

# --------------------------------------------------------
# Save Feature Columns
# --------------------------------------------------------

joblib.dump(list(X.columns), FEATURE_COLUMNS)

# --------------------------------------------------------
# Save Metrics
# --------------------------------------------------------

metrics = {
    "model": "Random Forest",
    "accuracy": float(accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
}

with open(RANDOM_FOREST_REPORT, "w") as file:
    json.dump(metrics, file, indent=4)

print("Metrics Saved.")

print()

print("=" * 60)
print("Training Finished Successfully")
print("=" * 60)