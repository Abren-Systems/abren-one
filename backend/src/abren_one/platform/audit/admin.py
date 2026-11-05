from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from abren_one.platform.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "action",
        "outcome",
        "actor_type",
        "actor_id",
        "organization_id",
        "target_type",
        "target_id",
    )
    list_filter = ("outcome", "actor_type", "action")
    search_fields = ("action", "target_type", "actor_id", "organization_id", "correlation_id")
    readonly_fields = [f.name for f in AuditEvent._meta.fields]
    ordering = ("-timestamp",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False
