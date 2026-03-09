"""
API views for the cloud gateway.
"""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.medical_records.models import MedicalRecord
from common.constants import ErrorMessages, SuccessMessages
from common.exceptions import CloudTransmissionError, EncryptionError, KeyLoadError
from common.permissions import IsDoctorOrAdmin

from .serializers import ForwardToCloudSerializer
from .services import CloudGatewayService

logger = logging.getLogger("apps.cloud_gateway")


def _client_ip(request: Request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class ForwardToCloudView(APIView):
    """POST /api/v1/records/forward-to-cloud/

    Decrypt a fog-side record, re-encrypt it for the cloud,
    and transmit via HTTPS.
    """

    permission_classes = [IsDoctorOrAdmin]

    def post(self, request: Request) -> Response:
        """Forward a medical record to the cloud service.

        Args:
            request: DRF request with ``record_id``.

        Returns:
            200 on success, 400/404/502 on failure.
        """
        serializer = ForwardToCloudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record_id = serializer.validated_data["record_id"]

        try:
            record = MedicalRecord.objects.get(pk=record_id)
        except MedicalRecord.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "not_found",
                        "message": ErrorMessages.RECORD_NOT_FOUND,
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = CloudGatewayService.forward_record(
                record=record,
                user=request.user,
                ip_address=_client_ip(request),
            )
        except KeyLoadError as exc:
            logger.error("Key load error during cloud forward: %s", exc)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "key_error",
                        "message": str(exc),
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except EncryptionError as exc:
            logger.error("Encryption error during cloud forward: %s", exc)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "encryption_error",
                        "message": ErrorMessages.ENCRYPTION_FAILED,
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except CloudTransmissionError as exc:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "cloud_unavailable",
                        "message": ErrorMessages.CLOUD_UNAVAILABLE,
                    },
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "success": True,
                "message": SuccessMessages.CLOUD_FORWARDED,
                "data": {
                    "record_id": str(record_id),
                    "attempts": result.attempts,
                    "cloud_status_code": result.status_code,
                },
            },
            status=status.HTTP_200_OK,
        )
