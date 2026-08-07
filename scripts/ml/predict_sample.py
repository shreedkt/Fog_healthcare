from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(BASE_DIR))

from apps.ai_prediction.predictor import RiskPredictor

predictor = RiskPredictor()

sample = {

    "age":55,

    "gender":1,

    "heart_rate":110,

    "systolic_bp":145,

    "temperature":37.5,

    "spo2":94,

    "respiratory_rate":22,

    "blood_sugar":180,

    "bmi":31,

    "smoking":1,

    "exercise_level":0,

    "cholesterol":240,

    "diastolic_bp":95,

}

print()

print("Predicting...")

print()

result = predictor.predict(sample)

print(result)