import uuid

from django.core.exceptions import PermissionDenied
from django.db import models


class AuditEvent(models.Model):
    """Immutable audit trail event (§8.3, §8.4).

    Records structured, append-only security and business events.
    Audit records cannot be modified or deleted.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_type = models.CharField(max_length=50)
    actor_id = models.UUIDField(null=True, blank=True)
    actor_role = models.CharField(max_length=50, null=True, blank=True)
    organization_id = models.UUIDField(null=True, blank=True)
    action = models.CharField(max_length=255)
    target_type = models.CharField(max_length=255)
    target_id = models.UUIDField()
    timestamp = models.DateTimeField(auto_now_add=True)
    correlation_id = models.UUIDField()
    outcome = models.CharField(max_length=50)  # success, denied, failed
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_event"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["organization_id", "-timestamp"]),
            models.Index(fields=["correlation_id"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.actor_type}:{self.actor_id} -> {self.action} ({self.outcome})"

    def save(self, *args, **kwargs) -> None:
        if self._state.adding is False:
            raise PermissionDenied("Audit events are immutable and cannot be updated (§8.4).")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        raise PermissionDenied("Audit events are immutable and cannot be deleted (§8.4).")
