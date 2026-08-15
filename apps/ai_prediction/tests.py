import json
from pathlib import Path

import joblib
from django.test import SimpleTestCase
from django.utils import timezone

from .predictor import RiskPredictor
from .serializers import PredictionSerializer
from .services import AIPredictionService


class PredictionPipelineTests(SimpleTestCase):
    sample = {
        "age": 62,
        "gender": "Female",
        "heart_rate": 160,
        "systolic_bp": 140,
        "cholesterol": 268,
    }

    def test_model_uses_only_independently_observed_features(self):
        model_dir = Path(__file__).resolve().parents[2] / "ml_model"
        features = joblib.load(model_dir / "encoders" / "feature_columns.pkl")

        self.assertEqual(
            features,
            [
                "age",
                "gender",
                "heart_rate",
                "systolic_bp",
                "cholesterol",
            ],
        )

    def test_predictor_accepts_raw_gender_and_returns_percentage(self):
        prediction = RiskPredictor().predict(self.sample)

        self.assertIn(prediction["risk_level"], {"Low", "Medium", "High"})
        self.assertGreaterEqual(prediction["confidence"], 0)
        self.assertLessEqual(prediction["confidence"], 100)

    def test_prediction_service_uses_measured_accuracy(self):
        service = AIPredictionService()
        result = service.predict(self.sample)
        report_path = (
            Path(__file__).resolve().parents[2]
            / "ml_model"
            / "reports"
            / "random_forest_metrics.json"
        )
        with report_path.open() as report_file:
            expected_accuracy = json.load(report_file)["accuracy"] * 100

        self.assertEqual(result["ai_model_accuracy"], round(expected_accuracy, 2))
        self.assertTrue(timezone.is_aware(result["prediction_time"]))

    def test_serializer_rejects_unknown_gender(self):
        serializer = PredictionSerializer(
            data={**self.sample, "gender": "unknown"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("gender", serializer.errors)
