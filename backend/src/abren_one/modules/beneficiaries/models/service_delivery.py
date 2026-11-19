import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Q

from abren_one.modules.beneficiaries.domain.value_objects import (
    DeliveryStatus,
    ServiceType,
)
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class ServiceDelivery(OrgOwnedMixin, TimestampMixin, models.Model):
    """Specific delivery of aid, training, or assistance to a beneficiary (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    beneficiary = models.ForeignKey(
        "beneficiaries.Beneficiary",
        on_delete=models.PROTECT,
        related_name="service_deliveries",
    )
    service_type = models.CharField(
        max_length=50,
        choices=[(s.value, s.name) for s in ServiceType],
    )
    status = models.CharField(
        max_length=50,
        choices=[(s.value, s.name) for s in DeliveryStatus],
        default=DeliveryStatus.DELIVERED.value,
        db_index=True,
    )
    delivery_date = models.DateField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    unit = models.CharField(max_length=50, blank=True, default="unit")
    notes = models.TextField(blank=True, default="")

    # Cross-module soft references (§4.4)
    program_id = models.UUIDField(null=True, blank=True, db_index=True)
    activity_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "beneficiaries_service_delivery"
        ordering = ["-delivery_date", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gte=0),
                name="service_delivery_quantity_non_negative",
            )
        ]

    def __str__(self) -> str:
        return f"{self.service_type} ({self.quantity} {self.unit}) to {self.beneficiary.display_name}"
