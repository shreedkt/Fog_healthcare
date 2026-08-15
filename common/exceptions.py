"""
Centralised exception definitions and DRF exception handler.

All custom exceptions inherit from ``FogHealthcareException`` so callers
can catch the entire family with a single ``except`` clause.
"""

from __future__ import annotations

import logging
from typing import Any

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("apps")


# ──────────────────────────────────────────────────────────────
# Base Exception
# ──────────────────────────────────────────────────────────────
class FogHealthcareException(Exception):
    """Root exception for the Fog Healthcare platform."""

    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


# ──────────────────────────────────────────────────────────────
# Encryption Exceptions
# ──────────────────────────────────────────────────────────────
class EncryptionError(FogHealthcareException):
    """Raised when encryption or decryption fails."""

    default_message = "Encryption operation failed."


class IntegrityVerificationError(FogHealthcareException):
    """Raised when the SHA-256 integrity hash does not match."""

    default_message = "Data integrity verification failed – payload may be tampered."


class KeyLoadError(FogHealthcareException):
    """Raised when an ECC key file cannot be loaded."""

    default_message = "Failed to load cryptographic key."


# ──────────────────────────────────────────────────────────────
# Record Exceptions
# ──────────────────────────────────────────────────────────────
class RecordNotFoundError(FogHealthcareException):
    """Raised when a medical record cannot be found."""

    default_message = "Medical record not found."


# ──────────────────────────────────────────────────────────────
# Cloud Gateway Exceptions
# ──────────────────────────────────────────────────────────────
class CloudTransmissionError(FogHealthcareException):
    """Raised when forwarding data to the cloud fails."""

    default_message = "Failed to transmit data to the cloud service."


# ──────────────────────────────────────────────────────────────
# Custom DRF Exception Handler
# ──────────────────────────────────────────────────────────────
def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    """Wrap DRF's default handler with structured JSON error envelopes.

    Response schema::

        {
            "success": false,
            "error": {
                "code": "<error_code>",
                "message": "<human readable message>"
            }
        }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code: str = getattr(exc, "default_code", "error")
        error_message: str = (
            response.data.get("detail", str(exc))
            if isinstance(response.data, dict)
            else str(response.data)
        )

        response.data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message,
            },
        }

        logger.warning(
            "API error %s – %s (view=%s)",
            response.status_code,
            error_message,
            context.get("view"),
        )

    return response
