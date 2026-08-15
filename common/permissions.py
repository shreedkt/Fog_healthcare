"""
Role-based DRF permission classes for the Fog Healthcare platform.

Roles are defined on the custom User model and enforced here
so views stay thin and declarative.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.constants import UserRole


class IsDoctorOrAdmin(BasePermission):
    """Allow DOCTOR or ADMIN roles."""

    message = "Doctor or Admin privileges required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user.is_authenticated and getattr(
            request.user, "role", None
        ) in (UserRole.DOCTOR, UserRole.ADMIN)


class CanReadRecords(BasePermission):
    """DOCTOR, NURSE, and ADMIN may read medical records."""

    message = "You do not have permission to view medical records."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user.is_authenticated and getattr(
            request.user, "role", None
        ) in (UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN)


class CanWriteRecords(BasePermission):
    """Only DOCTOR and ADMIN may create or update records."""

    message = "You do not have permission to create or modify medical records."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user.is_authenticated and getattr(
            request.user, "role", None
        ) in (UserRole.DOCTOR, UserRole.ADMIN)


class CanDeleteRecords(BasePermission):
    """Only ADMIN may soft-delete records."""

    message = "Only administrators may delete medical records."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.ADMIN
        )
