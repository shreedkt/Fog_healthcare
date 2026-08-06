import joblib

from django.conf import settings


class RiskPredictor:

    def __init__(self):

        self.model = joblib.load(settings.RISK_MODEL_PATH)

        self.gender_encoder = joblib.load(
            settings.ML_MODEL_DIR / "gender_encoder.pkl"
        )

        self.risk_encoder = joblib.load(
            settings.ML_MODEL_DIR / "risk_encoder.pkl"
        )

    def predict(
        self,
        age,
        gender,
        heart_rate,
        systolic_bp,
        diastolic_bp,
        temperature,
        spo2,
        respiratory_rate,
        blood_sugar,
    ):

        gender = self.gender_encoder.transform([gender])[0]

        prediction = self.model.predict(
            [[
                age,
                gender,
                heart_rate,
                systolic_bp,
                diastolic_bp,
                temperature,
                spo2,
                respiratory_rate,
                blood_sugar,
            ]]
        )[0]

        risk = self.risk_encoder.inverse_transform([prediction])[0]

        probability = max(self.model.predict_proba(
            [[
                age,
                gender,
                heart_rate,
                systolic_bp,
                diastolic_bp,
                temperature,
                spo2,
                respiratory_rate,
                blood_sugar,
            ]]
        )[0])

        return risk, probability