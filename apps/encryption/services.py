"""
Hybrid Encryption Service — AES-256-CBC + ECC (SECP256R1) + SHA-256.

Workflow
--------
**Encrypt (sender / IoT → Fog)**

1. Generate a random 256-bit AES session key.
2. Encrypt the plaintext payload with AES-256-CBC (random IV prepended).
3. Derive a shared secret via ECDH using the *recipient's* ECC public key
   and an ephemeral private key, then wrap the AES key with AES-KW (Key-Wrap).
4. Compute SHA-256 over the ciphertext for integrity.
5. Base64-encode all binary artefacts for safe JSON transport.

**Decrypt (Fog / Cloud)**

1. Re-derive the shared secret with ECDH using the recipient's *private* key
   and the sender's ephemeral *public* key.
2. Unwrap the AES session key.
3. Decrypt the ciphertext.
4. Verify the SHA-256 integrity hash.

Security notes
--------------
* A fresh ephemeral key-pair is created for **every** encryption call so that
  compromising one session key does not affect others (forward secrecy).
* ``os.urandom`` is used for all random bytes (CSPRNG).
* No secret material is ever logged.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes, keywrap, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.padding import PKCS7

from common.exceptions import (
    EncryptionError,
    IntegrityVerificationError,
    KeyLoadError,
)

logger = logging.getLogger("apps.encryption")

# AES-256 constants
AES_KEY_SIZE_BYTES: int = 32  # 256 bits
AES_BLOCK_SIZE_BITS: int = 128
IV_SIZE_BYTES: int = 16


# ──────────────────────────────────────────────────────────────
# Data containers
# ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class EncryptedPayload:
    """Immutable container for an encrypted message and its metadata."""

    ciphertext_b64: str
    encrypted_aes_key_b64: str
    ephemeral_public_key_b64: str
    integrity_hash: str

    def to_dict(self) -> dict[str, str]:
        return {
            "ciphertext": self.ciphertext_b64,
            "encrypted_aes_key": self.encrypted_aes_key_b64,
            "ephemeral_public_key": self.ephemeral_public_key_b64,
            "integrity_hash": self.integrity_hash,
        }


@dataclass(frozen=True)
class ECCKeyPair:
    """Container for a serialised ECC key-pair."""

    private_key_pem: bytes
    public_key_pem: bytes


# ──────────────────────────────────────────────────────────────
# Service
# ──────────────────────────────────────────────────────────────
class HybridEncryptionService:
    """AES-256-CBC + ECC SECP256R1 hybrid encryption.

    All methods are **static / class-level** — no mutable state is kept
    between calls to prevent accidental key reuse.
    """

    CURVE = ec.SECP256R1()
    HKDF_INFO = b"fog-healthcare-aes-key-wrap"

    # ── Key Management ───────────────────────────────────────

    @staticmethod
    def generate_key_pair() -> ECCKeyPair:
        """Generate a new ECC key-pair on the SECP256R1 curve.

        Returns:
            An ``ECCKeyPair`` with PEM-encoded private and public keys.
        """
        private_key = ec.generate_private_key(HybridEncryptionService.CURVE)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        logger.debug("Generated new ECC key-pair (SECP256R1).")
        return ECCKeyPair(private_key_pem=private_pem, public_key_pem=public_pem)

    @staticmethod
    def save_key_pair(key_pair: ECCKeyPair, directory: Path) -> None:
        """Persist a key-pair to disk.

        Args:
            key_pair: The key-pair to save.
            directory: Directory in which to write the PEM files.
        """
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "private_key.pem").write_bytes(key_pair.private_key_pem)
        (directory / "public_key.pem").write_bytes(key_pair.public_key_pem)
        logger.info("ECC key-pair saved to %s", directory)

    @staticmethod
    def load_public_key(path: Path) -> ec.EllipticCurvePublicKey:
        """Load a PEM-encoded ECC public key from *path*.

        Args:
            path: Filesystem path to the public key PEM file.

        Returns:
            An ``EllipticCurvePublicKey`` instance.

        Raises:
            KeyLoadError: If the file cannot be read or parsed.
        """
        try:
            pem_data = path.read_bytes()
            key = serialization.load_pem_public_key(pem_data)
            if not isinstance(key, ec.EllipticCurvePublicKey):
                raise KeyLoadError(f"Key at {path} is not an ECC public key.")
            return key
        except Exception as exc:
            raise KeyLoadError(f"Cannot load public key from {path}: {exc}") from exc

    @staticmethod
    def load_private_key(path: Path) -> ec.EllipticCurvePrivateKey:
        """Load a PEM-encoded ECC private key from *path*.

        Args:
            path: Filesystem path to the private key PEM file.

        Returns:
            An ``EllipticCurvePrivateKey`` instance.

        Raises:
            KeyLoadError: If the file cannot be read or parsed.
        """
        try:
            pem_data = path.read_bytes()
            key = serialization.load_pem_private_key(pem_data, password=None)
            if not isinstance(key, ec.EllipticCurvePrivateKey):
                raise KeyLoadError(f"Key at {path} is not an ECC private key.")
            return key
        except Exception as exc:
            raise KeyLoadError(f"Cannot load private key from {path}: {exc}") from exc

    # ── Encryption ───────────────────────────────────────────

    @classmethod
    def encrypt(
        cls,
        plaintext: str | bytes,
        recipient_public_key: ec.EllipticCurvePublicKey,
    ) -> EncryptedPayload:
        """Encrypt *plaintext* for the owner of *recipient_public_key*.

        Steps:
            1. Generate a random AES-256 session key.
            2. AES-256-CBC encrypt the plaintext (PKCS7 padded).
            3. Derive a wrapping key via ECDH + HKDF and wrap the AES key.
            4. Compute SHA-256 over the ciphertext.

        Args:
            plaintext: The data to encrypt (UTF-8 string or bytes).
            recipient_public_key: The recipient's ECC public key.

        Returns:
            An ``EncryptedPayload`` with Base64-encoded fields.

        Raises:
            EncryptionError: On any cryptographic failure.
        """
        try:
            if isinstance(plaintext, str):
                plaintext = plaintext.encode("utf-8")

            # 1 – Random AES session key + IV
            aes_key: bytes = os.urandom(AES_KEY_SIZE_BYTES)
            iv: bytes = os.urandom(IV_SIZE_BYTES)

            # 2 – AES-256-CBC encrypt
            padder = PKCS7(AES_BLOCK_SIZE_BITS).padder()
            padded: bytes = padder.update(plaintext) + padder.finalize()
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            ciphertext: bytes = encryptor.update(padded) + encryptor.finalize()
            ciphertext_with_iv: bytes = iv + ciphertext  # prepend IV

            # 3 – ECDH key agreement + AES key wrapping
            ephemeral_private = ec.generate_private_key(cls.CURVE)
            shared_secret = ephemeral_private.exchange(ec.ECDH(), recipient_public_key)
            wrapping_key = HKDF(
                algorithm=hashes.SHA256(),
                length=AES_KEY_SIZE_BYTES,
                salt=None,
                info=cls.HKDF_INFO,
            ).derive(shared_secret)
            wrapped_aes_key: bytes = keywrap.aes_key_wrap(wrapping_key, aes_key)

            ephemeral_pub_bytes: bytes = ephemeral_private.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            # 4 – Integrity hash (over ciphertext incl. IV)
            integrity_hash: str = hashlib.sha256(ciphertext_with_iv).hexdigest()

            payload = EncryptedPayload(
                ciphertext_b64=base64.b64encode(ciphertext_with_iv).decode(),
                encrypted_aes_key_b64=base64.b64encode(wrapped_aes_key).decode(),
                ephemeral_public_key_b64=base64.b64encode(ephemeral_pub_bytes).decode(),
                integrity_hash=integrity_hash,
            )
            logger.debug("Payload encrypted successfully (hash=%s).", integrity_hash[:12])
            return payload

        except Exception as exc:
            logger.error("Encryption failed: %s", exc)
            raise EncryptionError(f"Encryption failed: {exc}") from exc

    # ── Decryption ───────────────────────────────────────────

    @classmethod
    def decrypt(
        cls,
        encrypted_payload: EncryptedPayload | dict[str, str],
        recipient_private_key: ec.EllipticCurvePrivateKey,
        *,
        verify: bool = True,
    ) -> bytes:
        """Decrypt an ``EncryptedPayload`` using *recipient_private_key*.

        Args:
            encrypted_payload: Payload produced by ``encrypt()``, or an
                equivalent dict with keys ``ciphertext``,
                ``encrypted_aes_key``, ``ephemeral_public_key``, and
                ``integrity_hash``.
            recipient_private_key: The recipient's ECC private key.
            verify: If ``True`` (default), verify the integrity hash
                before decrypting.

        Returns:
            The original plaintext as ``bytes``.

        Raises:
            IntegrityVerificationError: If integrity check fails.
            EncryptionError: On any other cryptographic failure.
        """
        try:
            # Normalise input
            if isinstance(encrypted_payload, dict):
                ct_b64 = encrypted_payload["ciphertext"]
                key_b64 = encrypted_payload["encrypted_aes_key"]
                eph_b64 = encrypted_payload["ephemeral_public_key"]
                expected_hash = encrypted_payload["integrity_hash"]
            else:
                ct_b64 = encrypted_payload.ciphertext_b64
                key_b64 = encrypted_payload.encrypted_aes_key_b64
                eph_b64 = encrypted_payload.ephemeral_public_key_b64
                expected_hash = encrypted_payload.integrity_hash

            ciphertext_with_iv = base64.b64decode(ct_b64)
            wrapped_aes_key = base64.b64decode(key_b64)
            ephemeral_pub_bytes = base64.b64decode(eph_b64)

            # 1 – Integrity check
            if verify:
                cls.verify_integrity(ciphertext_with_iv, expected_hash)

            # 2 – ECDH shared secret
            ephemeral_pub = serialization.load_der_public_key(ephemeral_pub_bytes)
            if not isinstance(ephemeral_pub, ec.EllipticCurvePublicKey):
                raise EncryptionError("Ephemeral key is not an ECC public key.")

            shared_secret = recipient_private_key.exchange(ec.ECDH(), ephemeral_pub)
            wrapping_key = HKDF(
                algorithm=hashes.SHA256(),
                length=AES_KEY_SIZE_BYTES,
                salt=None,
                info=cls.HKDF_INFO,
            ).derive(shared_secret)

            # 3 – Unwrap AES key
            aes_key = keywrap.aes_key_unwrap(wrapping_key, wrapped_aes_key)

            # 4 – AES-256-CBC decrypt
            iv = ciphertext_with_iv[:IV_SIZE_BYTES]
            ciphertext = ciphertext_with_iv[IV_SIZE_BYTES:]
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded = decryptor.update(ciphertext) + decryptor.finalize()

            unpadder = PKCS7(AES_BLOCK_SIZE_BITS).unpadder()
            plaintext: bytes = unpadder.update(padded) + unpadder.finalize()

            logger.debug("Payload decrypted successfully.")
            return plaintext

        except IntegrityVerificationError:
            raise
        except Exception as exc:
            logger.error("Decryption failed: %s", exc)
            raise EncryptionError(f"Decryption failed: {exc}") from exc

    # ── Integrity ────────────────────────────────────────────

    @staticmethod
    def verify_integrity(
        data: bytes,
        expected_hash: str,
    ) -> bool:
        """Compare the SHA-256 hash of *data* against *expected_hash*.

        Args:
            data: The raw bytes to hash.
            expected_hash: The hex-encoded hash to compare against.

        Returns:
            ``True`` if the hashes match.

        Raises:
            IntegrityVerificationError: If the hashes do not match.
        """
        computed = hashlib.sha256(data).hexdigest()
        if computed != expected_hash:
            logger.warning(
                "Integrity check FAILED (expected=%s, computed=%s).",
                expected_hash[:12],
                computed[:12],
            )
            raise IntegrityVerificationError()
        logger.debug("Integrity check passed.")
        return True

    # ── Convenience ──────────────────────────────────────────

    @classmethod
    def encrypt_json(
        cls,
        data: dict[str, Any],
        recipient_public_key: ec.EllipticCurvePublicKey,
    ) -> EncryptedPayload:
        """Serialise *data* to JSON and encrypt it.

        A thin wrapper around ``encrypt()`` for dict payloads.
        """
        raw = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return cls.encrypt(raw, recipient_public_key)

    @classmethod
    def decrypt_json(
        cls,
        encrypted_payload: EncryptedPayload | dict[str, str],
        recipient_private_key: ec.EllipticCurvePrivateKey,
        *,
        verify: bool = True,
    ) -> dict[str, Any]:
        """Decrypt and deserialise a JSON payload.

        A thin wrapper around ``decrypt()`` for dict payloads.
        """
        plaintext = cls.decrypt(encrypted_payload, recipient_private_key, verify=verify)
        return json.loads(plaintext.decode("utf-8"))
