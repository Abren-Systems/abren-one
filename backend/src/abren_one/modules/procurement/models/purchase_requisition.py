import uuid
from decimal import Decimal

from django.db import models

from abren_one.modules.procurement.domain.value_objects import AuthorizationStatus
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class PurchaseRequisition(OrgOwnedMixin, TimestampMixin, models.Model):
    """Authorization lifecycle of an organizational need.

    Fulfillment is derived from OrderLineAllocation and GoodsReceiptItem quantities.
    """

    NUMBER_FIELD = "requisition_number"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requisition_number = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    authorization_status = models.CharField(
        max_length=30,
        choices=[(s.value, s.name) for s in AuthorizationStatus],
        db_index=True,
        default=AuthorizationStatus.DRAFT.value,
    )
    requested_by = models.UUIDField()
    approved_by = models.UUIDField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")
    currency = models.CharField(max_length=3, default="USD")
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "procurement_purchase_requisition"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "requisition_number"],
                name="unique_requisition_number_per_org",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.requisition_number} - {self.title}"

    @property
    def total_estimated_cost(self) -> Decimal:
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class RequisitionItem(TimestampMixin, models.Model):
    """Line-level item on a purchase requisition with operational attribution."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requisition = models.ForeignKey(
        "procurement.PurchaseRequisition",
        on_delete=models.CASCADE,
        related_name="items",
    )
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=50, default="each")
    estimated_unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    program_id = models.UUIDField(null=True, blank=True, db_index=True)
    activity_id = models.UUIDField(null=True, blank=True, db_index=True)
    department_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "procurement_requisition_item"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="req_item_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(estimated_unit_price__gte=0),
                name="req_item_price_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.description} ({self.quantity} {self.unit})"

    @property
    def line_total(self) -> Decimal:
        return Decimal(str(self.quantity)) * Decimal(str(self.estimated_unit_price))
