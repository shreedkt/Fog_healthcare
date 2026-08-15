"""
DRF serializers for medical records.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import MedicalRecord


class MedicalRecordCreateSerializer(serializers.Serializer):
    """
    Validate encrypted medical records and patient health parameters.
    """

    # ==========================================================
    # Existing Encryption Fields
    # ==========================================================

    patient_id = serializers.UUIDField(
        help_text="UUID of the patient."
    )

    encrypted_payload = serializers.CharField(
        help_text="Base64 encoded encrypted payload."
    )

    encrypted_aes_key = serializers.CharField(
        help_text="Encrypted AES Key."
    )

    ephemeral_public_key = serializers.CharField(
        help_text="Ephemeral ECC Public Key."
    )

    integrity_hash = serializers.CharField(
        max_length=64,
        help_text="SHA-256 Integrity Hash."
    )

    # ==========================================================
    # Independent clinical inputs used by the risk model
    # ==========================================================

    age = serializers.FloatField()

    gender = serializers.CharField()

    heart_rate = serializers.FloatField()

    systolic_bp = serializers.FloatField()

    cholesterol = serializers.FloatField()


class MedicalRecordResponseSerializer(serializers.ModelSerializer):
    """
    Read only Medical Record Response
    """

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

            # -------------------------
            # AI Prediction
            # -------------------------

            "risk_level",

            "risk_score",

            "recommendation",

            "prediction_time",

            "ai_model_name",

            "ai_model_accuracy",

        ]

        read_only_fields = fields