"""
Prepare Healthcare Dataset for AI Risk Prediction

This script:
1. Loads the UCI Heart Disease dataset
2. Cleans missing values
3. Generates additional IoT healthcare features
4. Creates a 3-class patient risk label
5. Saves the processed dataset
"""

from __future__ import annotations

import random

import numpy as np
import pandas as pd

from config import FINAL_DATASET, HEART_DATASET

# ----------------------------------------------------------
# Random Seed
# ----------------------------------------------------------

random.seed(42)
np.random.seed(42)

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
# Add IoT Features
# ----------------------------------------------------------

print("Generating IoT Healthcare Parameters...")

temperature = []

spo2 = []

respiratory_rate = []

blood_sugar = []

for _, row in df.iterrows():

    if row["target"] == 0:

        temperature.append(round(random.uniform(36.3, 37.2), 1))

        spo2.append(random.randint(96, 100))

        respiratory_rate.append(random.randint(12, 18))

        blood_sugar.append(random.randint(80, 120))

    elif row["target"] in [1, 2]:

        temperature.append(round(random.uniform(37.0, 38.0), 1))

        spo2.append(random.randint(92, 96))

        respiratory_rate.append(random.randint(18, 22))

        blood_sugar.append(random.randint(120, 170))

    else:

        temperature.append(round(random.uniform(38.0, 40.0), 1))

        spo2.append(random.randint(84, 92))

        respiratory_rate.append(random.randint(22, 30))

        blood_sugar.append(random.randint(170, 250))

df["temperature"] = temperature

df["spo2"] = spo2

df["respiratory_rate"] = respiratory_rate

df["blood_sugar"] = blood_sugar

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
        "temperature",
        "spo2",
        "respiratory_rate",
        "blood_sugar",
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