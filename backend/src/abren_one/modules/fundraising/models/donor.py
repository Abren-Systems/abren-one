import uuid

from django.db import models

from abren_one.modules.fundraising.domain.value_objects import (
    DonorStatus,
    DonorType,
)
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Donor(OrgOwnedMixin, TimestampMixin, models.Model):
    """An individual or institutional supporter (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    donor_type = models.CharField(
        max_length=50,
        choices=[(t.value, t.name) for t in DonorType],
        default=DonorType.INDIVIDUAL.value,
    )
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    status = models.CharField(
        max_length=50,
        choices=[(s.value, s.name) for s in DonorStatus],
        default=DonorStatus.ACTIVE.value,
        db_index=True,
    )

    class Meta:
        db_table = "fundraising_donors"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_organization_donor_name",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.donor_type})"

    @property
    def is_active(self) -> bool:
        return self.status == DonorStatus.ACTIVE.value
