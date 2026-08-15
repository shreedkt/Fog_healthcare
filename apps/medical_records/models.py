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
    """
    An encrypted medical record linked to a patient.

    The plaintext is NEVER stored.
    Only encrypted payloads and AI prediction metadata are stored.
    """
    ai_model_name = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    help_text="Machine learning model used."
)

    ai_model_accuracy = models.FloatField(
    blank=True,
    null=True,
    help_text="Model evaluation accuracy."
)

    patient_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True,
        help_text="Identifier of the patient this record belongs to.",
    )

    encrypted_payload = models.TextField(
        help_text="Base64 encoded AES encrypted medical payload.",
    )

    encrypted_aes_key = models.TextField(
        help_text="ECC wrapped AES session key.",
    )

    ephemeral_public_key = models.TextField(
        help_text="Ephemeral ECC public key.",
    )

    integrity_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 integrity hash.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="medical_records",
        help_text="User who uploaded the record.",
    )

    # ==========================================================
    # AI Prediction Information
    # ==========================================================

    risk_level = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Predicted Risk Level (Low, Medium, High).",
    )

    risk_score = models.FloatField(
        blank=True,
        null=True,
        help_text="Prediction confidence percentage.",
    )

    recommendation = models.TextField(
        blank=True,
        null=True,
        help_text="AI generated recommendation.",
    )

    prediction_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Time when AI prediction was generated.",
    )

    model_version = models.CharField(
        max_length=20,
        default="v1.0",
        help_text="Version of AI model.",
    )

    class Meta:
        db_table = "medical_records"
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["patient_id"], name="idx_patient_id"),
            models.Index(fields=["created_at"], name="idx_created_at"),
        ]

        verbose_name = "Medical Record"
        verbose_name_plural = "Medical Records"

    def __str__(self):
        return f"Record {self.pk} - {self.patient_id}"