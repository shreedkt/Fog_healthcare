"""
Evaluate Machine Learning Models

Compares all trained models and selects the best one.
"""

from __future__ import annotations

import json

import pandas as pd

from config import (
    RANDOM_FOREST_REPORT,
    XGBOOST_REPORT,
    MODEL_COMPARISON_CSV,
    FINAL_EVALUATION_REPORT,
    BEST_MODEL_REPORT,
)

print("=" * 60)
print("Loading Evaluation Reports")
print("=" * 60)

# ------------------------------------------------------
# Load Reports
# ------------------------------------------------------

with open(RANDOM_FOREST_REPORT, "r") as file:
    rf = json.load(file)

with open(XGBOOST_REPORT, "r") as file:
    xgb = json.load(file)

# ------------------------------------------------------
# Create Comparison Table
# ------------------------------------------------------

comparison = pd.DataFrame(
    [
        rf,
        xgb,
    ]
)

comparison.sort_values(
    by="accuracy",
    ascending=False,
    inplace=True,
)

comparison.reset_index(drop=True, inplace=True)

print()
print(comparison)

# ------------------------------------------------------
# Save CSV
# ------------------------------------------------------

comparison.to_csv(
    MODEL_COMPARISON_CSV,
    index=False,
)

print()
print("Model Comparison Saved")

# ------------------------------------------------------
# Best Model
# ------------------------------------------------------

best = comparison.iloc[0].to_dict()

print()
print("=" * 60)
print("Best Model")
print("=" * 60)

print(best)

# ------------------------------------------------------
# Save Best Model
# ------------------------------------------------------

with open(BEST_MODEL_REPORT, "w") as file:
    json.dump(best, file, indent=4)

# ------------------------------------------------------
# Save Final Evaluation
# ------------------------------------------------------

evaluation = {
    "models_evaluated": len(comparison),
    "best_model": best["model"],
    "accuracy": best["accuracy"],
    "precision": best["precision"],
    "recall": best["recall"],
    "f1_score": best["f1_score"],
}

with open(FINAL_EVALUATION_REPORT, "w") as file:
    json.dump(evaluation, file, indent=4)

print()
print("=" * 60)
print("Evaluation Completed Successfully")
print("=" * 60)