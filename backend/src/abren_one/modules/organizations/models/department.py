import uuid

from django.db import models

from abren_one.platform.common.models import TimestampMixin


class Department(TimestampMixin, models.Model):
    """Functional grouping within an organization or branch."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="departments",
    )
    branch = models.ForeignKey(
        "organizations.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "organizations_department"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_organization_department_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
