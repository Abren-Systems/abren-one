import uuid

from django.db import models

from abren_one.modules.procurement.domain.value_objects import (
    VendorType,
    VendorVerificationStatus,
)
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Vendor(OrgOwnedMixin, TimestampMixin, models.Model):
    """Supplier master serving both procurement and accounting."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    vendor_type = models.CharField(
        max_length=30,
        choices=[(t.value, t.name) for t in VendorType],
        default=VendorType.GOODS.value,
        db_index=True,
    )
    tax_id = models.CharField(max_length=100, blank=True, default="")
    country = models.CharField(max_length=3, default="", blank=True)
    contact_name = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    default_payment_terms = models.CharField(max_length=100, blank=True, default="")
    default_currency = models.CharField(max_length=3, default="USD")
    verification_status = models.CharField(
        max_length=30,
        choices=[(t.value, t.name) for t in VendorVerificationStatus],
        default=VendorVerificationStatus.UNVERIFIED.value,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    deactivation_reason = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "procurement_vendor"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "tax_id"],
                condition=~models.Q(tax_id=""),
                name="unique_vendor_tax_id_per_org",
            ),
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_vendor_name_per_org",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.vendor_type})"
