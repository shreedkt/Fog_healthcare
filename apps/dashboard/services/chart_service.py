from datetime import timedelta

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

        totals_by_day = {
            item["day"]: item["total"]
            for item in queryset
            if item["day"] is not None
        }

        if not totals_by_day:
            return {"labels": [], "values": []}

        labels = []
        values = []
        current_day = min(totals_by_day)
        final_day = max(totals_by_day)

        while current_day <= final_day:
            labels.append(current_day.strftime("%d %b"))
            values.append(totals_by_day.get(current_day, 0))
            current_day += timedelta(days=1)

        return {
            "labels": labels,
            "values": values,
        }