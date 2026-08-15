"""
DRF serializers for the users application.
"""

from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework import serializers

from common.constants import ErrorMessages

from .models import User


class LoginSerializer(serializers.Serializer):
    """Validates login credentials."""

    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="The user's username.",
    )
    password = serializers.CharField(
        max_length=128,
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text="The user's password.",
    )

    def validate(self, attrs: dict) -> dict:
        """Authenticate against Django's auth backend."""
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                ErrorMessages.INVALID_CREDENTIALS,
                code="invalid_credentials",
            )
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of a user."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "date_joined"]
        read_only_fields = fields
