import uuid
from decimal import Decimal

from django.db import models

from abren_one.modules.procurement.domain.value_objects import PurchaseOrderStatus
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class PurchaseOrder(OrgOwnedMixin, TimestampMixin, models.Model):
    """External commercial commitment to a supplier."""

    NUMBER_FIELD = "order_number"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=100)
    vendor = models.ForeignKey(
        "procurement.Vendor",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )
    requisition = models.ForeignKey(
        "procurement.PurchaseRequisition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_orders",
    )
    status = models.CharField(
        max_length=30,
        choices=[(s.value, s.name) for s in PurchaseOrderStatus],
        db_index=True,
        default=PurchaseOrderStatus.DRAFT.value,
    )
    currency = models.CharField(max_length=3, default="USD")
    payment_terms = models.CharField(max_length=100, blank=True, default="")
    issued_at = models.DateTimeField(null=True, blank=True)
    issued_by = models.UUIDField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.TextField(blank=True, default="")
    terms_and_conditions = models.TextField(blank=True, default="")
    cancellation_reason = models.TextField(blank=True, default="")
    cancelled_by = models.UUIDField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "procurement_purchase_order"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "order_number"],
                name="unique_order_number_per_org",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order_number} ({self.status})"

    @property
    def total_amount(self) -> Decimal:
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class PurchaseOrderItem(TimestampMixin, models.Model):
    """Line-level item on a purchase order."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(
        "procurement.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="items",
    )
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=50, default="each")
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = "procurement_purchase_order_item"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="po_item_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="po_item_price_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.description} ({self.quantity} {self.unit})"

    @property
    def line_total(self) -> Decimal:
        return Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
