from django.db.models import Count
from django.db.models.functions import TruncDate

from apps.medical_records.models import MedicalRecord


class ChartService:

    @staticmethod
    def risk_distribution():
        """
        Returns data for the Risk Distribution chart.
        """

        labels = [
            "Low",
            "Medium",
            "High",
        ]

        values = [
            MedicalRecord.objects.filter(
                risk_level="Low"
            ).count(),

            MedicalRecord.objects.filter(
                risk_level="Medium"
            ).count(),

            MedicalRecord.objects.filter(
                risk_level="High"
            ).count(),
        ]

        return {
            "labels": labels,
            "values": values,
        }

    @staticmethod
    def prediction_trend():
        """
        Returns data for the Prediction Trend chart.
        """

        queryset = (
            MedicalRecord.objects
            .exclude(prediction_time__isnull=True)
            .annotate(day=TruncDate("prediction_time"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )

        labels = []
        values = []

        for item in queryset:

            if item["day"] is None:
                continue

            labels.append(
                item["day"].strftime("%d %b")
            )

            values.append(
                item["total"]
            )

        return {
            "labels": labels,
            "values": values,
        }