from .predictor import RiskPredictor


predictor = RiskPredictor()


def predict_patient(patient):

    risk, score = predictor.predict(

        age=patient.age,

        gender=patient.gender,

        heart_rate=patient.heart_rate,

        systolic_bp=patient.systolic_bp,

        diastolic_bp=patient.diastolic_bp,

        temperature=patient.temperature,

        spo2=patient.spo2,

        respiratory_rate=patient.respiratory_rate,

        blood_sugar=patient.blood_sugar,

    )

    recommendation = {

        "Low": "Routine monitoring.",

        "Medium": "Doctor consultation recommended.",

        "High": "Immediate medical attention required.",

    }[risk]

    return risk, score, recommendation