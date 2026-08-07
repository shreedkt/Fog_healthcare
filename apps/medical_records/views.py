"""
API views for medical records.

All business logic is delegated to ``MedicalRecordService``.
"""

from __future__ import annotations

import logging
from uuid import UUID

from rest_framework import status
from rest_framework import request
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants import ErrorMessages, SuccessMessages
from common.exceptions import IntegrityVerificationError, RecordNotFoundError
from common.permissions import CanDeleteRecords, CanReadRecords, CanWriteRecords

from .serializers import MedicalRecordCreateSerializer, MedicalRecordResponseSerializer
from .services import MedicalRecordService

logger = logging.getLogger("apps.medical_records")


def _client_ip(request: Request) -> str:
    """Extract the client IP address."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class RecordCreateView(APIView):
    """POST /api/v1/records/create/

    Accepts an encrypted medical payload and stores it.
    """

    permission_classes = [CanWriteRecords]

    def post(self, request: Request) -> Response:
        """Create a new encrypted medical record.

        Args:
            request: DRF request with encrypted payload fields.

        Returns:
            201 on success, 400 on validation / integrity failure.
        """
        serializer = MedicalRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            validated_data = serializer.validated_data

            patient_data = {
                "age": validated_data.pop("age"),
                "gender": validated_data.pop("gender"),
                "heart_rate": validated_data.pop("heart_rate"),
                "systolic_bp": validated_data.pop("systolic_bp"),
                "diastolic_bp": validated_data.pop("diastolic_bp"),
                "temperature": validated_data.pop("temperature"),
                "spo2": validated_data.pop("spo2"),
                "respiratory_rate": validated_data.pop("respiratory_rate"),
                "blood_sugar": validated_data.pop("blood_sugar"),
                "bmi": validated_data.pop("bmi"),
                "smoking": validated_data.pop("smoking"),
                "exercise_level": validated_data.pop("exercise_level"),
                "cholesterol": validated_data.pop("cholesterol"),
            }

            record = MedicalRecordService.create_record(
                **validated_data,
                patient_data=patient_data,
                created_by=request.user,
                ip_address=_client_ip(request),
            )
        except IntegrityVerificationError:
            return Response(
                {"success": False, "error": {"code": "integrity_failed", "message": ErrorMessages.INTEGRITY_FAILED}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": SuccessMessages.RECORD_CREATED,
                "data": MedicalRecordResponseSerializer(record).data,
            },
            status=status.HTTP_201_CREATED,
        )


class RecordDetailView(APIView):
    """GET /api/v1/records/<id>/
    DELETE /api/v1/records/<id>/

    Retrieve or soft-delete a single record.
    """

    def get_permissions(self) -> list:
        if self.request.method == "DELETE":
            return [CanDeleteRecords()]
        return [CanReadRecords()]

    def get(self, request: Request, record_id: UUID) -> Response:
        """Retrieve a medical record by its UUID.

        Args:
            request: DRF request.
            record_id: UUID path parameter.

        Returns:
            200 with record data, or 404.
        """
        try:
            record = MedicalRecordService.get_record(
                record_id=record_id,
                user=request.user,
                ip_address=_client_ip(request),
            )
        except RecordNotFoundError:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": ErrorMessages.RECORD_NOT_FOUND}},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "data": MedicalRecordResponseSerializer(record).data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, record_id: UUID) -> Response:
        """Soft-delete a medical record (ADMIN only).

        Args:
            request: DRF request.
            record_id: UUID path parameter.

        Returns:
            200 on success, 404 if not found.
        """
        try:
            MedicalRecordService.soft_delete_record(
                record_id=record_id,
                user=request.user,
                ip_address=_client_ip(request),
            )
        except RecordNotFoundError:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": ErrorMessages.RECORD_NOT_FOUND}},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "message": SuccessMessages.RECORD_DELETED,
            },
            status=status.HTTP_200_OK,
        )


class PatientRecordsView(APIView):
    """GET /api/v1/records/patient/<patient_id>/

    Retrieve all records for a given patient.
    """

    permission_classes = [CanReadRecords]

    def get(self, request: Request, patient_id: UUID) -> Response:
        """List all medical records for a patient.

        Args:
            request: DRF request.
            patient_id: UUID path parameter.

        Returns:
            200 with list of records.
        """
        records = MedicalRecordService.get_records_by_patient(
            patient_id=patient_id,
            user=request.user,
            ip_address=_client_ip(request),
        )

        return Response(
            {
                "success": True,
                "count": len(records),
                "data": MedicalRecordResponseSerializer(records, many=True).data,
            },
            status=status.HTTP_200_OK,
        )