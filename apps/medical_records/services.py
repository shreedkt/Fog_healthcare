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

from django.db import transaction

from apps.audit.services import AuditService
from apps.encryption.services import HybridEncryptionService
from common.constants import AuditAction
from common.exceptions import IntegrityVerificationError, RecordNotFoundError

from .models import MedicalRecord

logger = logging.getLogger("apps.medical_records")


class MedicalRecordService:
    """Encapsulates all medical-record business logic."""

    @staticmethod
    def create_record(
        *,
        patient_id: UUID,
        encrypted_payload: str,
        encrypted_aes_key: str,
        ephemeral_public_key: str,
        integrity_hash: str,
        created_by: Any,
        ip_address: str = "unknown",
    ) -> MedicalRecord:
        """Persist a new encrypted medical record after integrity check.

        Args:
            patient_id: The patient's UUID.
            encrypted_payload: Base64-encoded AES ciphertext.
            encrypted_aes_key: Base64-encoded wrapped AES key.
            ephemeral_public_key: Base64-encoded ephemeral ECC public key.
            integrity_hash: Expected SHA-256 hex digest.
            created_by: The authenticated User instance.
            ip_address: Client IP for audit logging.

        Returns:
            The newly created ``MedicalRecord``.

        Raises:
            IntegrityVerificationError: If the hash does not match.
        """
        # Verify integrity before persisting
        ciphertext_bytes = base64.b64decode(encrypted_payload)
        HybridEncryptionService.verify_integrity(ciphertext_bytes, integrity_hash)

        with transaction.atomic():
            record = MedicalRecord.objects.create(
                patient_id=patient_id,
                encrypted_payload=encrypted_payload,
                encrypted_aes_key=encrypted_aes_key,
                ephemeral_public_key=ephemeral_public_key,
                integrity_hash=integrity_hash,
                created_by=created_by,
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
        """Retrieve a single record by ID and log the access.

        Args:
            record_id: The UUID of the record.
            user: The authenticated User instance.
            ip_address: Client IP for audit logging.

        Returns:
            The ``MedicalRecord`` instance.

        Raises:
            RecordNotFoundError: If the record does not exist or is soft-deleted.
        """
        try:
            record = MedicalRecord.objects.select_related("created_by").get(
                pk=record_id
            )
        except MedicalRecord.DoesNotExist:
            raise RecordNotFoundError(f"Record {record_id} not found.")

        AuditService.log(
            user=user,
            action=AuditAction.READ,
            record=record,
            ip_address=ip_address,
        )
        return record

    @staticmethod
    def get_records_by_patient(
        patient_id: UUID,
        user: Any,
        ip_address: str = "unknown",
    ) -> list[MedicalRecord]:
        """Retrieve all active records for a given patient.

        Args:
            patient_id: The patient's UUID.
            user: The authenticated User instance.
            ip_address: Client IP for audit logging.

        Returns:
            Queryset of ``MedicalRecord`` instances.
        """
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
        """Soft-delete a medical record.

        Args:
            record_id: The UUID of the record.
            user: The authenticated User instance.
            ip_address: Client IP for audit logging.

        Raises:
            RecordNotFoundError: If the record does not exist.
        """
        try:
            record = MedicalRecord.objects.get(pk=record_id)
        except MedicalRecord.DoesNotExist:
            raise RecordNotFoundError(f"Record {record_id} not found.")

        record.soft_delete()

        AuditService.log(
            user=user,
            action=AuditAction.DELETE,
            record=record,
            ip_address=ip_address,
        )
        logger.info("Record %s soft-deleted by %s", record_id, user.username)
