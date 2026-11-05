import uuid

from django.db import models

from abren_one.modules.programs.domain.value_objects import ProgramStatus
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Program(OrgOwnedMixin, TimestampMixin, models.Model):
    """Long-running strategic initiative grouping related projects (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in ProgramStatus],
        default=ProgramStatus.ACTIVE.value,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "programs_program"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_organization_program_name",
            )
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def is_active(self) -> bool:
        return self.status == ProgramStatus.ACTIVE.value
