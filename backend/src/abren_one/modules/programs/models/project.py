import uuid

from django.db import models

from abren_one.modules.programs.domain.value_objects import ProjectStatus
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Project(OrgOwnedMixin, TimestampMixin, models.Model):
    """Time-bound effort with deliverables, belonging to a program."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.PROTECT,
        related_name="projects",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in ProjectStatus],
        default=ProjectStatus.PLANNING.value,
    )
    budget_currency = models.CharField(max_length=3, default="USD")

    class Meta:
        db_table = "programs_project"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["program", "name"],
                name="unique_program_project_name",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.program.name})"
