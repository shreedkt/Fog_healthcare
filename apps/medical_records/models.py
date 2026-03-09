"""
Medical record models.

Stores encrypted payloads received from IoT devices via the Fog node.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from common.mixins import BaseModel


class MedicalRecord(BaseModel):
    """An encrypted medical record linked to a patient.

    The plaintext is **never** stored — only the AES-encrypted payload,
    the ECC-wrapped AES key, and the SHA-256 integrity hash.
    """

    patient_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True,
        help_text="Identifier of the patient this record belongs to.",
    )
    encrypted_payload = models.TextField(
        help_text="Base64-encoded AES-256-CBC ciphertext (IV prepended).",
    )
    encrypted_aes_key = models.TextField(
        help_text="Base64-encoded AES session key wrapped with ECC.",
    )
    ephemeral_public_key = models.TextField(
        help_text="Base64-encoded ephemeral ECC public key used during encryption.",
    )
    integrity_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 hex digest of the ciphertext for tamper detection.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="medical_records",
        help_text="The user who submitted this record.",
    )

    class Meta:
        db_table = "medical_records"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient_id"], name="idx_patient_id"),
            models.Index(fields=["created_at"], name="idx_created_at"),
        ]
        verbose_name = "medical record"
        verbose_name_plural = "medical records"

    def __str__(self) -> str:
        return f"Record {self.pk} (patient={self.patient_id})"
