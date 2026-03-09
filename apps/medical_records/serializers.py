"""
DRF serializers for medical records.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import MedicalRecord


class MedicalRecordCreateSerializer(serializers.Serializer):
    """Validates incoming encrypted payloads from IoT / client devices.

    The client has already encrypted the data; the API stores it as-is
    after verifying the integrity hash.
    """

    patient_id = serializers.UUIDField(
        help_text="UUID of the patient.",
    )
    encrypted_payload = serializers.CharField(
        help_text="Base64-encoded AES ciphertext.",
    )
    encrypted_aes_key = serializers.CharField(
        help_text="Base64-encoded wrapped AES key.",
    )
    ephemeral_public_key = serializers.CharField(
        help_text="Base64-encoded ephemeral ECC public key.",
    )
    integrity_hash = serializers.CharField(
        max_length=64,
        help_text="SHA-256 hex digest of the ciphertext.",
    )


class MedicalRecordResponseSerializer(serializers.ModelSerializer):
    """Read-only representation of a stored medical record."""

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient_id",
            "encrypted_payload",
            "encrypted_aes_key",
            "ephemeral_public_key",
            "integrity_hash",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
