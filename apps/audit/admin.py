"""
Django admin for audit logs.
"""

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "record_id", "ip_address")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "record_id", "ip_address")
    readonly_fields = (
        "id",
        "user",
        "action",
        "record_id",
        "ip_address",
        "details",
        "timestamp",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):  # type: ignore[override]
        return False

    def has_change_permission(self, request, obj=None):  # type: ignore[override]
        return False

    def has_delete_permission(self, request, obj=None):  # type: ignore[override]
        return False
