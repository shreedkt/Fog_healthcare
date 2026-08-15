"""
Patient Dashboard Service
"""

from apps.medical_records.models import MedicalRecord


class PatientService:

    @staticmethod
    def recent_predictions(limit=5):

        return (

            MedicalRecord.objects

            .only(

                "patient_id",

                "risk_level",

                "risk_score",

                "prediction_time",

            )

            .order_by("-created_at")[:limit]

        )