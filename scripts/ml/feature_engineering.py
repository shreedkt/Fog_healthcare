"""
Feature Engineering Pipeline

This script:
1. Loads the processed healthcare dataset
2. Encodes categorical variables
3. Saves encoders
4. Saves feature column names
5. Saves the final engineered dataset
"""

from __future__ import annotations

import joblib
import pandas as pd

from sklearn.preprocessing import LabelEncoder

from config import (
    FINAL_DATASET,
    ENCODER_DIR,
    FEATURE_COLUMNS,
    GENDER_ENCODER,
    LABEL_ENCODER,
)

# --------------------------------------------------------
# Load Dataset
# --------------------------------------------------------

print("=" * 60)
print("Loading Processed Dataset...")
print("=" * 60)

df = pd.read_csv(FINAL_DATASET)

print(f"Records Loaded : {len(df)}")

# --------------------------------------------------------
# Encode Gender
# --------------------------------------------------------

print("Encoding Gender...")

gender_encoder = LabelEncoder()

df["gender"] = gender_encoder.fit_transform(df["gender"])

# --------------------------------------------------------
# Encode Risk
# --------------------------------------------------------

print("Encoding Risk Level...")

risk_encoder = LabelEncoder()

df["risk_level"] = risk_encoder.fit_transform(df["risk_level"])

# --------------------------------------------------------
# Save Encoders
# --------------------------------------------------------

print("Saving Encoders...")

ENCODER_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(gender_encoder, GENDER_ENCODER)

joblib.dump(risk_encoder, LABEL_ENCODER)

joblib.dump(
    [column for column in df.columns if column != "risk_level"],
    FEATURE_COLUMNS,
)

# --------------------------------------------------------
# Save Engineered Dataset
# --------------------------------------------------------

df.to_csv(FINAL_DATASET, index=False)

print()

print("=" * 60)
print("Feature Engineering Completed Successfully")
print("=" * 60)

print()

print(df.head())

print()

print(f"Dataset Saved : {FINAL_DATASET}")

print(f"Total Features : {len(df.columns)-1}")

print(f"Training Records : {len(df)}")