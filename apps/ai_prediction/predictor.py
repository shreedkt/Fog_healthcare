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

GENDER_ENCODER_PATH = MODEL_DIR / "encoders" / "gender_encoder.pkl"


class RiskPredictor:
    """
    Loads the trained ML model and performs predictions.
    """

    def __init__(self):

        self.model = joblib.load(MODEL_PATH)

        self.features = joblib.load(FEATURE_COLUMNS_PATH)

        self.encoder = joblib.load(LABEL_ENCODER_PATH)

        self.encoder_gender = joblib.load(GENDER_ENCODER_PATH)

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

        model_input = dict(patient_data)
        gender = model_input.get("gender")

        if isinstance(gender, str):
            normalized_gender = gender.strip().title()
            if normalized_gender in {"0", "1"}:
                model_input["gender"] = int(normalized_gender)
            elif normalized_gender in set(self.encoder_gender.classes_):
                model_input["gender"] = int(
                    self.encoder_gender.transform([normalized_gender])[0]
                )
            else:
                raise ValueError("gender must be 'Female', 'Male', 0, or 1")
        elif gender in (0, 1, 0.0, 1.0):
            model_input["gender"] = int(gender)
        else:
            raise ValueError("gender must be 'Female', 'Male', 0, or 1")

        missing_features = [
            feature for feature in self.features if feature not in model_input
        ]
        if missing_features:
            raise ValueError(
                f"Missing prediction features: {', '.join(missing_features)}"
            )

        # Ignore API fields not used by the trained model.
        df = pd.DataFrame(
            [{feature: model_input[feature] for feature in self.features}]
        )

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