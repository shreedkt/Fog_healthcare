"""
Service layer for user authentication.

Keeps views thin – all session management logic lives here.
"""

from __future__ import annotations

import logging

from django.contrib.auth import login, logout
from django.http import HttpRequest

from .models import User

logger = logging.getLogger("apps.users")


class AuthService:
    """Handles session-based login / logout."""

    @staticmethod
    def login(request: HttpRequest, user: User) -> None:
        """Create a server-side session for the authenticated user.

        Args:
            request: The current HTTP request.
            user: The authenticated User instance.
        """
        login(request, user)
        logger.info(
            "User '%s' (role=%s) logged in from %s",
            user.username,
            user.role,
            AuthService._client_ip(request),
        )

    @staticmethod
    def logout(request: HttpRequest) -> None:
        """Destroy the current session.

        Args:
            request: The current HTTP request.
        """
        username = getattr(request.user, "username", "anonymous")
        logout(request)
        logger.info("User '%s' logged out.", username)

    @staticmethod
    def _client_ip(request: HttpRequest) -> str:
        """Extract the client IP from the request (handles proxies)."""
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
