"""
Dashboard Analytics Service
"""

from apps.medical_records.models import MedicalRecord


class AnalyticsService:

    @staticmethod
    def get_summary():

        qs = MedicalRecord.objects.all()

        return {

            "total_records": qs.count(),

            "total_patients": qs.values("patient_id").distinct().count(),

            "low_risk": qs.filter(risk_level="Low").count(),

            "medium_risk": qs.filter(risk_level="Medium").count(),

            "high_risk": qs.filter(risk_level="High").count(),

        }