"""
Prepare Healthcare Dataset for AI Risk Prediction

This script:
1. Loads the UCI Heart Disease dataset
2. Cleans missing values
3. Keeps independently observed clinical features
4. Creates a 3-class patient risk label
5. Saves the processed dataset
"""

from __future__ import annotations

import pandas as pd

from config import FINAL_DATASET, HEART_DATASET

# ----------------------------------------------------------
# Original UCI Dataset Columns
# ----------------------------------------------------------

COLUMN_NAMES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target",
]

# ----------------------------------------------------------
# Load Dataset
# ----------------------------------------------------------

print("Loading UCI Heart Disease Dataset...")

df = pd.read_csv(
    HEART_DATASET,
    header=None,
    names=COLUMN_NAMES,
    na_values="?",
)

print(f"Dataset Loaded : {len(df)} records")

# ----------------------------------------------------------
# Missing Values
# ----------------------------------------------------------

print("Cleaning missing values...")

df.dropna(inplace=True)

df.reset_index(drop=True, inplace=True)

print(f"Remaining Records : {len(df)}")

# ----------------------------------------------------------
# Rename Columns
# ----------------------------------------------------------

df.rename(
    columns={
        "sex": "gender",
        "trestbps": "systolic_bp",
        "thalach": "heart_rate",
        "chol": "cholesterol",
    },
    inplace=True,
)

# ----------------------------------------------------------
# Gender Mapping
# ----------------------------------------------------------

df["gender"] = df["gender"].map(
    {
        1: "Male",
        0: "Female",
    }
)

# ----------------------------------------------------------
# Risk Level
# ----------------------------------------------------------

print("Generating Risk Labels...")

risk = []

for value in df["target"]:

    if value == 0:

        risk.append("Low")

    elif value in [1, 2]:

        risk.append("Medium")

    else:

        risk.append("High")

df["risk_level"] = risk

# ----------------------------------------------------------
# Select Required Columns
# ----------------------------------------------------------

final_df = df[
    [
        "age",
        "gender",
        "heart_rate",
        "systolic_bp",
        "cholesterol",
        "risk_level",
    ]
]

# ----------------------------------------------------------
# Save Dataset
# ----------------------------------------------------------

FINAL_DATASET.parent.mkdir(
    parents=True,
    exist_ok=True,
)

final_df.to_csv(
    FINAL_DATASET,
    index=False,
)

print()

print("=" * 50)

print("Dataset Prepared Successfully")

print("=" * 50)

print()

print(final_df.head())

print()

print(f"Saved To : {FINAL_DATASET}")

print(f"Total Records : {len(final_df)}")