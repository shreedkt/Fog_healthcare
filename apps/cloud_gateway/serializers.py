"""
DRF serializer for cloud-forwarding requests.
"""

from __future__ import annotations

from rest_framework import serializers


class ForwardToCloudSerializer(serializers.Serializer):
    """Accepts the UUID of the record to forward to the cloud."""

    record_id = serializers.UUIDField(
        help_text="UUID of the medical record to re-encrypt and forward.",
    )
