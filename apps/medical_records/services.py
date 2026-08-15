"""
Service layer for medical record operations.

All business logic for creating, retrieving, and validating records
is encapsulated here so that views remain thin.
"""

from __future__ import annotations

import base64
import logging
from typing import Any
from uuid import UUID

from django.conf import settings
from django.db import transaction

from apps.audit.services import AuditService
from apps.encryption.services import HybridEncryptionService
from apps.ai_prediction.services import AIPredictionService

from common.constants import AuditAction
from common.exceptions import (
    IntegrityVerificationError,
    RecordNotFoundError,
)

from .models import MedicalRecord

logger = logging.getLogger("apps.medical_records")


class MedicalRecordService:
    """Medical Record Business Logic."""

    @staticmethod
    def create_record(
        *,
        patient_id: UUID,
        encrypted_payload: str,
        encrypted_aes_key: str,
        ephemeral_public_key: str,
        integrity_hash: str,
        created_by: Any,
        patient_data: dict,
        ip_address: str = "unknown",
    ) -> MedicalRecord:

        # ------------------------------------
        # Verify Encryption Integrity
        # ------------------------------------

        ciphertext_bytes = base64.b64decode(encrypted_payload)
        HybridEncryptionService.verify_integrity(
            ciphertext_bytes,
            integrity_hash,
        )

        # ------------------------------------
        # AI Prediction
        # ------------------------------------

        ai_service = AIPredictionService()

        prediction = ai_service.predict(patient_data)

        # ------------------------------------
        # Save Record
        # ------------------------------------

        with transaction.atomic():

            record = MedicalRecord.objects.create(

                patient_id=patient_id,

                encrypted_payload=encrypted_payload,

                encrypted_aes_key=encrypted_aes_key,

                ephemeral_public_key=ephemeral_public_key,

                integrity_hash=integrity_hash,

                created_by=created_by,

                risk_level=prediction["risk_level"],

                risk_score=prediction["risk_score"],

                recommendation=prediction["recommendation"],

                prediction_time=prediction["prediction_time"],

                ai_model_name=prediction["ai_model_name"],

                ai_model_accuracy=prediction["ai_model_accuracy"],
            )

            AuditService.log(
                user=created_by,
                action=AuditAction.CREATE,
                record=record,
                ip_address=ip_address,
            )

        logger.info(
            "Record %s created for patient %s by %s",
            record.pk,
            patient_id,
            created_by.username,
        )

        return record

    @staticmethod
    def get_record(
        record_id: UUID,
        user: Any,
        ip_address: str = "unknown",
    ) -> MedicalRecord:

        try:
            record = MedicalRecord.objects.select_related(
                "created_by"
            ).get(pk=record_id)

        except MedicalRecord.DoesNotExist:
            raise RecordNotFoundError(
                f"Record {record_id} not found."
            )

        AuditService.log(
            user=user,
            action=AuditAction.READ,
            record=record,
            ip_address=ip_address,
        )

        return record

    @staticmethod
    def get_decrypted_record(
        record_id: UUID,
        user: Any,
        ip_address: str = "unknown",
    ) -> dict[str, Any]:
        record = MedicalRecordService.get_record(
            record_id=record_id,
            user=user,
            ip_address=ip_address,
        )
        private_key = HybridEncryptionService.load_private_key(
            settings.FOG_ECC_PRIVATE_KEY_PATH
        )
        data = HybridEncryptionService.decrypt_json(
            {
                "ciphertext": record.encrypted_payload,
                "encrypted_aes_key": record.encrypted_aes_key,
                "ephemeral_public_key": record.ephemeral_public_key,
                "integrity_hash": record.integrity_hash,
            },
            private_key,
        )

        return {
            "record_id": record.pk,
            "patient_id": record.patient_id,
            "created_by": record.created_by,
            "created_at": record.created_at,
            "risk_level": record.risk_level,
            "risk_score": record.risk_score,
            "data": data,
        }

    @staticmethod
    def get_records_by_patient(
        patient_id: UUID,
        user: Any,
        ip_address: str = "unknown",
    ) -> list[MedicalRecord]:

        records = list(
            MedicalRecord.objects.select_related("created_by")
            .filter(patient_id=patient_id)
            .order_by("-created_at")
        )

        if records:

            AuditService.log(
                user=user,
                action=AuditAction.READ,
                record=records[0],
                ip_address=ip_address,
                details=f"Bulk read for patient {patient_id} ({len(records)} records)",
            )

        return records

    @staticmethod
    def soft_delete_record(
        record_id: UUID,
        user: Any,
        ip_address: str = "unknown",
    ) -> None:

        try:
            record = MedicalRecord.objects.get(pk=record_id)

        except MedicalRecord.DoesNotExist:
            raise RecordNotFoundError(
                f"Record {record_id} not found."
            )

        record.soft_delete()

        AuditService.log(
            user=user,
            action=AuditAction.DELETE,
            record=record,
            ip_address=ip_address,
        )

        logger.info(
            "Record %s soft-deleted by %s",
            record_id,
            user.username,
        )