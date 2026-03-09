#!/usr/bin/env python
"""
Generate ECC key-pairs for the Fog and Cloud nodes.

Usage:
    python scripts/generate_keys.py

Creates:
    keys/fog_private_key.pem
    keys/fog_public_key.pem
    keys/cloud_private_key.pem
    keys/cloud_public_key.pem
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running as standalone script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure Django before importing any app modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django  # noqa: E402
django.setup()  # noqa: E402

from apps.encryption.services import HybridEncryptionService  # noqa: E402


def main() -> None:
    """Generate and save key-pairs for both fog and cloud nodes."""
    keys_dir = PROJECT_ROOT / "keys"
    keys_dir.mkdir(exist_ok=True)

    # ── Fog Node Keys ────────────────────────────────────────
    print("🔑 Generating Fog Node ECC key-pair…")
    fog_kp = HybridEncryptionService.generate_key_pair()
    (keys_dir / "fog_private_key.pem").write_bytes(fog_kp.private_key_pem)
    (keys_dir / "fog_public_key.pem").write_bytes(fog_kp.public_key_pem)
    print(f"   ✔ Saved to {keys_dir / 'fog_private_key.pem'}")
    print(f"   ✔ Saved to {keys_dir / 'fog_public_key.pem'}")

    # ── Cloud Node Keys ──────────────────────────────────────
    print("🔑 Generating Cloud Node ECC key-pair…")
    cloud_kp = HybridEncryptionService.generate_key_pair()
    (keys_dir / "cloud_private_key.pem").write_bytes(cloud_kp.private_key_pem)
    (keys_dir / "cloud_public_key.pem").write_bytes(cloud_kp.public_key_pem)
    print(f"   ✔ Saved to {keys_dir / 'cloud_private_key.pem'}")
    print(f"   ✔ Saved to {keys_dir / 'cloud_public_key.pem'}")

    print("\n✅ All keys generated successfully.")
    print("⚠️  Keep private keys secure and never commit them to version control.")


if __name__ == "__main__":
    main()
