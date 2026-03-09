"""
Service layer for the dashboard application.

Encapsulates all business logic for record retrieval, decryption,
and audit logging so that views remain thin and declarative.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from django.conf import settings
from django.http import HttpRequest

from apps.audit.services import AuditService
from apps.encryption.services import HybridEncryptionService
from apps.medical_records.models import MedicalRecord
from apps.users.constants import UserRole
from common.constants import AuditAction
from common.exceptions import (
    EncryptionError,
    IntegrityVerificationError,
    KeyLoadError,
    RecordNotFoundError,
)

logger = logging.getLogger("apps.dashboard")


@dataclass(frozen=True)
class DecryptedRecord:
    """Read-only container returned to templates after decryption."""

    record_id: UUID
    patient_id: UUID
    data: dict[str, Any]
    created_by: str
    created_at: str


@dataclass(frozen=True)
class DashboardStats:
    """Aggregate numbers displayed on the home page."""

    total_records: int
    total_patients: int


class DashboardService:
    """Orchestrates dashboard read operations."""

    # -- Aggregate statistics ------------------------------------------------

    @staticmethod
    def get_stats() -> DashboardStats:
        """Return high-level counts for the home page.

        Returns:
            A ``DashboardStats`` instance.
        """
        total_records = MedicalRecord.objects.count()
        total_patients = (
            MedicalRecord.objects.values("patient_id").distinct().count()
        )
        return DashboardStats(
            total_records=total_records,
            total_patients=total_patients,
        )

    # -- Record listing ------------------------------------------------------

    @staticmethod
    def list_records(
        patient_id_filter: str | None = None,
    ) -> list[MedicalRecord]:
        """Return active medical records, optionally filtered by patient.

        Args:
            patient_id_filter: If provided, filter records to this patient UUID.

        Returns:
            Queryset of ``MedicalRecord`` instances ordered by most recent first.
        """
        qs = MedicalRecord.objects.select_related("created_by").order_by(
            "-created_at"
        )
        if patient_id_filter:
            try:
                pid = UUID(patient_id_filter)
                qs = qs.filter(patient_id=pid)
            except ValueError:
                logger.warning(
                    "Invalid patient_id filter ignored: %s", patient_id_filter
                )
        return list(qs)

    # -- Single record with decryption ---------------------------------------

    @staticmethod
    def get_decrypted_record(
        record_id: UUID,
        user: Any,
        request: HttpRequest,
    ) -> DecryptedRecord:
        """Fetch, verify integrity, decrypt, and audit-log a single record.

        Args:
            record_id: Primary key of the ``MedicalRecord``.
            user: The authenticated ``User`` instance.
            request: The originating HTTP request (for IP extraction).

        Returns:
            A ``DecryptedRecord`` with the plaintext data dict.

        Raises:
            RecordNotFoundError: If the record does not exist.
            IntegrityVerificationError: If the SHA-256 hash does not match.
            EncryptionError: If decryption fails for any other reason.
            KeyLoadError: If the fog private key cannot be loaded.
        """
        # 1 -- Fetch
        try:
            record = MedicalRecord.objects.select_related("created_by").get(
                pk=record_id
            )
        except MedicalRecord.DoesNotExist:
            raise RecordNotFoundError(f"Record {record_id} not found.")

        # 2 -- Load fog private key
        fog_private_key = HybridEncryptionService.load_private_key(
            settings.FOG_ECC_PRIVATE_KEY_PATH
        )

        # 3 -- Decrypt (integrity verified inside decrypt)
        payload_dict: dict[str, str] = {
            "ciphertext": record.encrypted_payload,
            "encrypted_aes_key": record.encrypted_aes_key,
            "ephemeral_public_key": record.ephemeral_public_key,
            "integrity_hash": record.integrity_hash,
        }
        decrypted_data: dict[str, Any] = HybridEncryptionService.decrypt_json(
            payload_dict, fog_private_key, verify=True
        )

        # 4 -- Audit
        ip_address = _client_ip(request)
        AuditService.log(
            user=user,
            action=AuditAction.READ,
            record=record,
            ip_address=ip_address,
            details="Dashboard record view (decrypted)",
        )

        return DecryptedRecord(
            record_id=record.pk,
            patient_id=record.patient_id,
            data=decrypted_data,
            created_by=record.created_by.username,
            created_at=record.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        )

    # -- Role checks ---------------------------------------------------------

    @staticmethod
    def can_view_records(user: Any) -> bool:
        """Return ``True`` if the user's role permits viewing records."""
        return getattr(user, "role", None) in (
            UserRole.DOCTOR,
            UserRole.NURSE,
            UserRole.ADMIN,
        )

    @staticmethod
    def can_modify_records(user: Any) -> bool:
        """Return ``True`` if the user's role permits creating/updating records."""
        return getattr(user, "role", None) in (
            UserRole.DOCTOR,
            UserRole.ADMIN,
        )


def _client_ip(request: HttpRequest) -> str:
    """Extract client IP, respecting reverse-proxy headers."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")
