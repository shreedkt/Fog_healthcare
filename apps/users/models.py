"""
Custom User model with role-based access.
"""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .constants import UserRole


class UserManager(BaseUserManager["User"]):
    """Manager for the custom User model."""

    def create_user(
        self,
        username: str,
        password: str | None = None,
        role: str = UserRole.NURSE,
        **extra_fields: object,
    ) -> "User":
        """Create and return a regular user with a hashed password."""
        if not username:
            raise ValueError("A username is required.")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> "User":
        """Create and return a superuser with ADMIN role."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    """Custom user with UUID primary key and role field."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.NURSE,
        db_index=True,
        help_text="Determines the user's access level.",
    )

    objects: UserManager = UserManager()  # type: ignore[assignment]

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

    # ── Convenience helpers ──────────────────────────────────

    @property
    def is_doctor(self) -> bool:
        return self.role == UserRole.DOCTOR

    @property
    def is_nurse(self) -> bool:
        return self.role == UserRole.NURSE

    @property
    def is_admin_role(self) -> bool:
        return self.role == UserRole.ADMIN
