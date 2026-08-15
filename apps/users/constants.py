"""
Constants for the users application.
"""

from django.db import models


class UserRole(models.TextChoices):
    """Available roles for platform users."""

    DOCTOR = "DOCTOR", "Doctor"
    NURSE = "NURSE", "Nurse"
    ADMIN = "ADMIN", "Admin"
