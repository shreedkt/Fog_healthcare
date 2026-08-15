"""
Service layer for user authentication.

Keeps views thin – all session management logic lives here.
"""

from __future__ import annotations

import logging

from django.contrib.auth import login, logout
from django.http import HttpRequest

from common.http import get_client_ip

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
            get_client_ip(request),
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
