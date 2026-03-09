"""
Reusable model mixins for the Secure Fog Healthcare platform.

Provides UUID primary keys, timestamps, and soft-delete behaviour
so that every app model stays consistent.
"""

import uuid

from django.db import models


class UUIDPrimaryKeyMixin(models.Model):
    """Replaces the default auto-incrementing PK with a UUID4."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Universally unique identifier.",
    )

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """Adds created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Default manager that filters out soft-deleted rows."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Manager that returns *all* rows including soft-deleted ones."""

    pass


class SoftDeleteMixin(models.Model):
    """Provides a boolean ``is_deleted`` flag instead of hard-deleting rows."""

    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Mark the record as deleted without removing it from the database."""
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.save(update_fields=["is_deleted", "updated_at"])


class BaseModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Convenience base that combines UUID PK + timestamps + soft delete."""

    class Meta:
        abstract = True
