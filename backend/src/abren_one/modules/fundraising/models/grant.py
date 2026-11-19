import uuid

from django.db import models
from django.db.models import F, Q

from abren_one.modules.fundraising.domain.value_objects import GrantStatus
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Grant(OrgOwnedMixin, TimestampMixin, models.Model):
    """Institutional funding agreement (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        "fundraising.Donor",
        on_delete=models.PROTECT,
        related_name="grants",
    )
    title = models.CharField(max_length=255)
    reference_code = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=[(s.value, s.name) for s in GrantStatus],
        default=GrantStatus.PROPOSED.value,
        db_index=True,
    )
    # Cross-module soft reference (§4.4)
    program_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "fundraising_grants"
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "reference_code"],
                name="unique_organization_grant_reference",
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name="grant_total_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")),
                name="grant_end_date_gte_start_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} [{self.reference_code}] ({self.total_amount} {self.currency})"

    @property
    def is_active(self) -> bool:
        return self.status in {GrantStatus.AWARDED.value, GrantStatus.ACTIVE.value}
