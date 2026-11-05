import uuid

from django.db import models

from abren_one.platform.common.models import TimestampMixin


class Branch(TimestampMixin, models.Model):
    """Physical or logical subdivision of an organization (e.g. regional office)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="branches",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_headquarters = models.BooleanField(default=False)

    class Meta:
        db_table = "organizations_branch"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_organization_branch_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
