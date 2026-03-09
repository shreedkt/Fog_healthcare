"""
Audit trail model.

Every access to medical data is logged here for compliance and forensics.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from common.constants import AuditAction


class AuditLog(models.Model):
    """Immutable record of a data-access event."""

    ACTION_CHOICES = [
        (AuditAction.READ, "Read"),
        (AuditAction.CREATE, "Create"),
        (AuditAction.UPDATE, "Update"),
        (AuditAction.DELETE, "Delete"),
        (AuditAction.FORWARD, "Forward to Cloud"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
        help_text="User who performed the action.",
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="The type of action performed.",
    )
    record_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="UUID of the medical record involved.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the client.",
    )
    details = models.TextField(
        blank=True,
        default="",
        help_text="Additional context about the action.",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"], name="idx_audit_user_ts"),
            models.Index(fields=["record_id", "timestamp"], name="idx_audit_record_ts"),
        ]
        verbose_name = "audit log"
        verbose_name_plural = "audit logs"

    def __str__(self) -> str:
        username = self.user.username if self.user else "system"
        return f"[{self.timestamp}] {username} – {self.action} – {self.record_id}"
