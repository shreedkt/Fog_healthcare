"""
Management command to create default demo users.

Usage:
    python manage.py seed_users
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.users.constants import UserRole
from apps.users.models import User


class Command(BaseCommand):
    help = "Create default demo users (doctor1, nurse1, admin1) for development."

    DEMO_USERS = [
        {"username": "doctor1", "password": "doctor1pass", "role": UserRole.DOCTOR, "email": "doctor1@fog.local"},
        {"username": "nurse1", "password": "nurse1pass", "role": UserRole.NURSE, "email": "nurse1@fog.local"},
        {"username": "admin1", "password": "admin1pass", "role": UserRole.ADMIN, "email": "admin1@fog.local"},
    ]

    def handle(self, *args: object, **options: object) -> None:
        for user_data in self.DEMO_USERS:
            username = user_data["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"  ⏭  User '{username}' already exists – skipping."))
                continue

            User.objects.create_user(
                username=user_data["username"],
                password=user_data["password"],
                role=user_data["role"],
                email=user_data["email"],
            )
            self.stdout.write(self.style.SUCCESS(f"  ✔  Created user '{username}' (role={user_data['role']})"))

        self.stdout.write(self.style.SUCCESS("\n✅ Seed users ready."))
