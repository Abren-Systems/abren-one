import uuid

from django.db import models
from django.db.models import Q

from abren_one.modules.fundraising.domain.value_objects import (
    DonationStatus,
    PaymentMethod,
)
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Donation(OrgOwnedMixin, TimestampMixin, models.Model):
    """Monetary contribution received from a supporter (§4.1, §4.4, §Appendix B)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        "fundraising.Donor",
        on_delete=models.PROTECT,
        related_name="donations",
    )
    grant = models.ForeignKey(
        "fundraising.Grant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    received_at = models.DateTimeField()
    payment_method = models.CharField(
        max_length=50,
        choices=[(m.value, m.name) for m in PaymentMethod],
        default=PaymentMethod.BANK_TRANSFER.value,
    )
    reference = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(
        max_length=50,
        choices=[(s.value, s.name) for s in DonationStatus],
        default=DonationStatus.RECEIVED.value,
    )
    # Cross-module soft reference (§4.4)
    program_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "fundraising_donations"
        ordering = ["-received_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="donation_amount_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"Donation {self.id}: {self.amount} {self.currency} from {self.donor.name}"

    @property
    def is_confirmed(self) -> bool:
        return self.status == DonationStatus.CONFIRMED.value
