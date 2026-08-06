"""
Feature Engineering Pipeline

This script:
1. Loads the processed healthcare dataset
2. Creates additional healthcare features
3. Encodes categorical variables
4. Saves encoders
5. Saves feature column names
6. Saves the final engineered dataset
"""

from __future__ import annotations

import random
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
# Random Seed
# --------------------------------------------------------

random.seed(42)

# --------------------------------------------------------
# Load Dataset
# --------------------------------------------------------

print("=" * 60)
print("Loading Processed Dataset...")
print("=" * 60)

df = pd.read_csv(FINAL_DATASET)

print(f"Records Loaded : {len(df)}")

# --------------------------------------------------------
# BMI Generation
# --------------------------------------------------------

print("Generating BMI...")

bmi = []

for _, row in df.iterrows():

    if row["risk_level"] == "Low":
        bmi.append(round(random.uniform(18.5, 24.9), 1))

    elif row["risk_level"] == "Medium":
        bmi.append(round(random.uniform(25.0, 29.9), 1))

    else:
        bmi.append(round(random.uniform(30.0, 40.0), 1))

df["bmi"] = bmi

# --------------------------------------------------------
# Smoking Status
# --------------------------------------------------------

print("Generating Smoking Status...")

smoking = []

for _, row in df.iterrows():

    if row["risk_level"] == "Low":
        smoking.append(random.choice(["No", "No", "No", "Yes"]))

    elif row["risk_level"] == "Medium":
        smoking.append(random.choice(["No", "Yes", "Yes"]))

    else:
        smoking.append(random.choice(["Yes", "Yes", "Yes", "No"]))

df["smoking"] = smoking

# --------------------------------------------------------
# Exercise Level
# --------------------------------------------------------

print("Generating Exercise Level...")

exercise = []

for _, row in df.iterrows():

    if row["risk_level"] == "Low":
        exercise.append(random.choice(["High", "Medium"]))

    elif row["risk_level"] == "Medium":
        exercise.append(random.choice(["Medium", "Low"]))

    else:
        exercise.append("Low")

df["exercise_level"] = exercise

# --------------------------------------------------------
# Cholesterol
# --------------------------------------------------------

print("Generating Cholesterol...")

cholesterol = []

for _, row in df.iterrows():

    if row["risk_level"] == "Low":
        cholesterol.append(random.randint(150, 200))

    elif row["risk_level"] == "Medium":
        cholesterol.append(random.randint(200, 240))

    else:
        cholesterol.append(random.randint(240, 320))

df["cholesterol"] = cholesterol

# --------------------------------------------------------
# Diastolic Blood Pressure
# --------------------------------------------------------

print("Generating Diastolic Blood Pressure...")

diastolic = []

for systolic in df["systolic_bp"]:

    if systolic < 120:
        diastolic.append(random.randint(70, 79))

    elif systolic < 140:
        diastolic.append(random.randint(80, 89))

    else:
        diastolic.append(random.randint(90, 110))

df["diastolic_bp"] = diastolic

# --------------------------------------------------------
# Encode Gender
# --------------------------------------------------------

print("Encoding Gender...")

gender_encoder = LabelEncoder()

df["gender"] = gender_encoder.fit_transform(df["gender"])

# --------------------------------------------------------
# Encode Smoking
# --------------------------------------------------------

print("Encoding Smoking...")

smoking_encoder = LabelEncoder()

df["smoking"] = smoking_encoder.fit_transform(df["smoking"])

# --------------------------------------------------------
# Encode Exercise
# --------------------------------------------------------

print("Encoding Exercise Level...")

exercise_encoder = LabelEncoder()

df["exercise_level"] = exercise_encoder.fit_transform(df["exercise_level"])

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

joblib.dump(list(df.columns[:-1]), FEATURE_COLUMNS)

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