"""
Service layer for the audit trail.
"""

from __future__ import annotations

import logging
from typing import Any

from .models import AuditLog

logger = logging.getLogger("apps.audit")


class AuditService:
    """Writes immutable audit records for every data-access event."""

    @staticmethod
    def log(
        *,
        user: Any,
        action: str,
        record: Any | None = None,
        ip_address: str = "unknown",
        details: str = "",
    ) -> AuditLog:
        """Create an audit log entry.

        Args:
            user: The authenticated ``User`` instance.
            action: One of the ``AuditAction`` constants.
            record: The ``MedicalRecord`` involved (optional).
            ip_address: Client IP address.
            details: Free-text details.

        Returns:
            The created ``AuditLog`` instance.
        """
        record_id = getattr(record, "pk", None)

        entry = AuditLog.objects.create(
            user=user,
            action=action,
            record_id=record_id,
            ip_address=ip_address if ip_address != "unknown" else None,
            details=details,
        )

        logger.info(
            "AUDIT | user=%s action=%s record=%s ip=%s | %s",
            user.username,
            action,
            record_id,
            ip_address,
            details or "-",
        )
        return entry
