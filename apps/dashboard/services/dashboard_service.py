"""
Dashboard Service

Provides all data required by dashboard templates.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from django.http import HttpRequest

from apps.medical_records.models import MedicalRecord
from apps.medical_records.services import MedicalRecordService
from common.http import get_client_ip

from .analytics_service import AnalyticsService
from .chart_service import ChartService
from .patient_service import PatientService


BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_REPORT_FILE = (
    BASE_DIR
    / "ml_model"
    / "reports"
    / "random_forest_metrics.json"
)


class DashboardService:

    @staticmethod
    def get_dashboard():
        """
        Returns everything required by dashboard/home.html.
        """

        summary = AnalyticsService.get_summary()

        patients = PatientService.recent_predictions()

        risk_chart = ChartService.risk_distribution()

        trend_chart = ChartService.prediction_trend()

        ai = {
            "model": "Unknown",
            "accuracy": 0.0,
        }

        if MODEL_REPORT_FILE.exists():
            with open(MODEL_REPORT_FILE, "r") as file:
                model = json.load(file)

            ai = {
                "model": model.get("model", "Unknown"),
                "accuracy": round(
                    model.get("accuracy", 0) * 100,
                    2,
                ),
            }

        return {
            "summary": summary,
    "patients": patients,
    "risk_chart": json.dumps(risk_chart),
    "trend_chart": json.dumps(trend_chart),
    "ai": ai,
        }

    @staticmethod
    def list_records(patient_id_filter=None):
        """
        Returns all medical records.
        """

        queryset = MedicalRecord.objects.only(
            "id",
            "patient_id",
            "risk_level",
            "risk_score",
            "prediction_time",
            "created_at",
            "created_by",
            "ai_model_name",
        )


        if patient_id_filter:
            queryset = queryset.filter(
                patient_id=patient_id_filter
            )

        return queryset.order_by("-created_at")

    @staticmethod
    def get_decrypted_record(
        record_id: UUID,
        user,
        request: HttpRequest,
    ):
        """
        Returns decrypted record.
        """

        record = MedicalRecordService.get_decrypted_record(
            record_id=record_id,
            user=user,
            ip_address=get_client_ip(request),
        )
        clinical_inputs = record.get("data", {}).get(
            "clinical_inputs",
            {},
        )
        acronyms = {"bp": "BP", "id": "ID"}
        record["clinical_input_rows"] = [
            {
                "label": " ".join(
                    acronyms.get(word.lower(), word.title())
                    for word in key.split("_")
                ),
                "value": value,
            }
            for key, value in clinical_inputs.items()
        ]
        return record