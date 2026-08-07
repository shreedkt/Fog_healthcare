"""
AI Prediction Engine

Loads the trained ML model and predicts
patient health risk.
"""

from pathlib import Path

import joblib
import pandas as pd

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_DIR = BASE_DIR / "ml_model"

MODEL_PATH = MODEL_DIR / "trained" / "random_forest.pkl"

FEATURE_COLUMNS_PATH = MODEL_DIR / "encoders" / "feature_columns.pkl"

LABEL_ENCODER_PATH = MODEL_DIR / "encoders" / "label_encoder.pkl"


class RiskPredictor:
    """
    Loads the trained ML model and performs predictions.
    """

    def __init__(self):

        self.model = joblib.load(MODEL_PATH)

        self.features = joblib.load(FEATURE_COLUMNS_PATH)

        self.encoder = joblib.load(LABEL_ENCODER_PATH)

    def predict(self, patient_data: dict) -> dict:
        """
        Predict patient risk.

        Args:
            patient_data:
                Dictionary containing patient vitals.

        Returns:
            {
                "risk_level": "...",
                "confidence": 94.5
            }
        """

        # Convert dictionary into DataFrame
        df = pd.DataFrame([patient_data])

        # Ensure feature order matches training
        df = df[self.features]

        # Prediction
        prediction = self.model.predict(df)[0]

        probabilities = self.model.predict_proba(df)[0]

        confidence = float(max(probabilities))

        risk = self.encoder.inverse_transform([prediction])[0]

        return {

            "risk_level": risk,

            "confidence": round(confidence * 100, 2),

        }