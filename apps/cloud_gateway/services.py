"""
Cloud Gateway service.

Responsible for:
1. Decrypting the payload stored at the fog node.
2. Re-encrypting it under the *cloud's* ECC public key.
3. Transmitting the re-encrypted payload to the cloud API via HTTPS.
4. Retrying on transient failures.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from django.conf import settings

from apps.audit.services import AuditService
from apps.encryption.services import HybridEncryptionService
from apps.medical_records.models import MedicalRecord
from common.constants import AuditAction
from common.exceptions import CloudTransmissionError, EncryptionError, KeyLoadError

logger = logging.getLogger("apps.cloud_gateway")


@dataclass(frozen=True)
class TransmissionResult:
    """Outcome of a cloud transmission attempt."""

    success: bool
    status_code: int | None
    message: str
    attempts: int


class CloudGatewayService:
    """Decrypts fog-side data and re-encrypts + forwards it to the cloud."""

    @classmethod
    def forward_record(
        cls,
        record: MedicalRecord,
        user: Any,
        ip_address: str = "unknown",
    ) -> TransmissionResult:
        """Decrypt a record at the fog, re-encrypt for the cloud, and POST.

        Args:
            record: The ``MedicalRecord`` to forward.
            user: The authenticated User performing the action.
            ip_address: Client IP for audit.

        Returns:
            A ``TransmissionResult`` describing the outcome.

        Raises:
            CloudTransmissionError: If all retry attempts fail.
            KeyLoadError: If ECC keys cannot be loaded.
            EncryptionError: If encryption / decryption fails.
        """
        fog_private_key_path: Path = settings.FOG_ECC_PRIVATE_KEY_PATH
        cloud_public_key_path: Path = settings.CLOUD_ECC_PUBLIC_KEY_PATH

        # 1 – Load keys
        fog_private_key = HybridEncryptionService.load_private_key(fog_private_key_path)
        cloud_public_key = HybridEncryptionService.load_public_key(cloud_public_key_path)

        # 2 – Decrypt on the fog side
        payload_dict = {
            "ciphertext": record.encrypted_payload,
            "encrypted_aes_key": record.encrypted_aes_key,
            "ephemeral_public_key": record.ephemeral_public_key,
            "integrity_hash": record.integrity_hash,
        }
        plaintext: bytes = HybridEncryptionService.decrypt(
            payload_dict, fog_private_key, verify=True
        )

        # 3 – Re-encrypt for the cloud
        cloud_payload = HybridEncryptionService.encrypt(plaintext, cloud_public_key)

        # 4 – Transmit with retries
        result = cls._transmit(cloud_payload.to_dict(), record.pk)

        # 5 – Audit
        AuditService.log(
            user=user,
            action=AuditAction.FORWARD,
            record=record,
            ip_address=ip_address,
            details=f"Cloud transmission {'succeeded' if result.success else 'FAILED'} "
            f"after {result.attempts} attempt(s). "
            f"status_code={result.status_code}",
        )

        if not result.success:
            raise CloudTransmissionError(result.message)

        return result

    # ── Private helpers ──────────────────────────────────────

    @classmethod
    def _transmit(
        cls,
        payload: dict[str, str],
        record_id: Any,
    ) -> TransmissionResult:
        """POST *payload* to the cloud API with retry logic.

        Args:
            payload: The re-encrypted payload dict.
            record_id: Used for logging context.

        Returns:
            A ``TransmissionResult``.
        """
        cloud_url: str = settings.CLOUD_API_URL
        timeout: int = settings.CLOUD_API_TIMEOUT
        max_retries: int = settings.CLOUD_API_MAX_RETRIES

        if not cloud_url:
            return TransmissionResult(
                success=False,
                status_code=None,
                message="CLOUD_API_URL is not configured.",
                attempts=0,
            )

        last_error: str = ""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Cloud TX attempt %d/%d for record %s → %s",
                    attempt,
                    max_retries,
                    record_id,
                    cloud_url,
                )
                response = requests.post(
                    cloud_url,
                    json=payload,
                    timeout=timeout,
                    verify=True,  # SSL verification enabled
                    headers={"Content-Type": "application/json"},
                )

                if response.ok:
                    logger.info(
                        "Cloud TX succeeded (status=%d, record=%s).",
                        response.status_code,
                        record_id,
                    )
                    return TransmissionResult(
                        success=True,
                        status_code=response.status_code,
                        message="Transmission successful.",
                        attempts=attempt,
                    )

                last_error = (
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                logger.warning(
                    "Cloud TX attempt %d failed: %s", attempt, last_error
                )

            except requests.exceptions.Timeout:
                last_error = f"Request timed out after {timeout}s."
                logger.warning("Cloud TX attempt %d timed out.", attempt)

            except requests.exceptions.ConnectionError as exc:
                last_error = f"Connection error: {exc}"
                logger.warning("Cloud TX attempt %d connection error: %s", attempt, exc)

            except requests.exceptions.RequestException as exc:
                last_error = f"Request error: {exc}"
                logger.error("Cloud TX attempt %d unexpected error: %s", attempt, exc)

            # Exponential back-off between retries
            if attempt < max_retries:
                wait = 2 ** (attempt - 1)
                logger.debug("Waiting %ds before retry…", wait)
                time.sleep(wait)

        return TransmissionResult(
            success=False,
            status_code=None,
            message=f"All {max_retries} attempts failed. Last error: {last_error}",
            attempts=max_retries,
        )
