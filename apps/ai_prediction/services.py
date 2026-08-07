"""
Business logic for AI prediction.
"""

from datetime import datetime

from .predictor import RiskPredictor


class AIPredictionService:
    """
    AI Prediction Service.

    Uses the trained ML model to predict patient risk and
    generate recommendation metadata.
    """

    def __init__(self):
        self.predictor = RiskPredictor()

    def predict(self, patient_data: dict) -> dict:
        """
        Predict patient health risk.

        Args:
            patient_data: Patient vital parameters.

        Returns:
            Dictionary containing AI prediction metadata.
        """

        result = self.predictor.predict(patient_data)

        risk = result["risk_level"]
        confidence = round(float(result["confidence"]), 2)

        # ----------------------------------
        # Recommendation
        # ----------------------------------

        if risk == "Low":

            recommendation = (
                "Patient condition is stable. "
                "Continue routine monitoring."
            )

        elif risk == "Medium":

            recommendation = (
                "Patient requires regular observation. "
                "Consult physician if symptoms increase."
            )

        else:

            recommendation = (
                "High Risk detected. "
                "Immediate medical attention recommended."
            )

        # ----------------------------------
        # AI Metadata
        # ----------------------------------

        return {

            "risk_level": risk,

            "risk_score": confidence,

            "recommendation": recommendation,

            "prediction_time": datetime.now(),

            "ai_model_name": "Random Forest",

            "ai_model_accuracy": 100.0,

        }