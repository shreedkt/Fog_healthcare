"""
Django admin for medical records.
"""

from django.contrib import admin

from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "patient_id", "created_by", "created_at", "is_deleted")
    list_filter = ("is_deleted", "created_at")
    search_fields = ("patient_id", "integrity_hash")
    readonly_fields = (
        "id",
        "encrypted_payload",
        "encrypted_aes_key",
        "ephemeral_public_key",
        "integrity_hash",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
