import uuid

from django.db import models

from abren_one.modules.programs.domain.value_objects import ActivityStatus
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Activity(OrgOwnedMixin, TimestampMixin, models.Model):
    """Specific operational task or action within a project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "programs.Project",
        on_delete=models.PROTECT,
        related_name="activities",
    )
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in ActivityStatus],
        default=ActivityStatus.PENDING.value,
    )
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "programs_activity"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.name} [{self.status}]"
