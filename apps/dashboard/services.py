"""
Dashboard business logic.
"""

from apps.medical_records.models import MedicalRecord


class DashboardService:
    """Provides dashboard statistics."""

    @staticmethod
    def get_dashboard_data():

        total_records = MedicalRecord.objects.count()

        low_risk = MedicalRecord.objects.filter(
            risk_level="Low"
        ).count()

        medium_risk = MedicalRecord.objects.filter(
            risk_level="Medium"
        ).count()

        high_risk = MedicalRecord.objects.filter(
            risk_level="High"
        ).count()

        latest_predictions = (
            MedicalRecord.objects
            .select_related("created_by")
            .order_by("-prediction_time")[:10]
        )

        latest_model = (
            MedicalRecord.objects
            .exclude(ai_model_name__isnull=True)
            .exclude(ai_model_name="")
            .order_by("-prediction_time")
            .first()
        )

        return {

            "total_records": total_records,

            "low_risk": low_risk,

            "medium_risk": medium_risk,

            "high_risk": high_risk,

            "latest_predictions": latest_predictions,

            "model_name": (
                latest_model.ai_model_name
                if latest_model
                else "Random Forest"
            ),

            "model_accuracy": (
                latest_model.ai_model_accuracy
                if latest_model
                else 0
            ),
        }