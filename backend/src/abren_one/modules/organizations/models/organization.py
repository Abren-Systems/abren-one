import uuid

from django.db import models

from abren_one.modules.organizations.domain.value_objects import OrganizationStatus
from abren_one.platform.common.models import TimestampMixin


class Organization(TimestampMixin, models.Model):
    """Top-level tenant boundary entity (§5.1).

    All tenant-scoped records belong to an organization.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in OrganizationStatus],
        default=OrganizationStatus.ACTIVE.value,
        db_index=True,
    )

    class Meta:
        db_table = "organizations_organization"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def is_active(self) -> bool:
        return self.status == OrganizationStatus.ACTIVE.value
