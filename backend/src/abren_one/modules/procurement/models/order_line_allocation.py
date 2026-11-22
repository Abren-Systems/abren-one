import uuid

from django.db import models

from abren_one.platform.common.models import TimestampMixin


class OrderLineAllocation(TimestampMixin, models.Model):
    """Explicit, quantity-tracked traceability between requisition items and PO items."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requisition_item = models.ForeignKey(
        "procurement.RequisitionItem",
        on_delete=models.PROTECT,
        related_name="allocations",
    )
    po_item = models.ForeignKey(
        "procurement.PurchaseOrderItem",
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    allocated_quantity = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "procurement_order_line_allocation"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(allocated_quantity__gt=0),
                name="allocation_quantity_positive",
            ),
            models.UniqueConstraint(
                fields=["requisition_item", "po_item"],
                name="unique_allocation_per_line_pair",
            ),
        ]

    def __str__(self) -> str:
        return f"Alloc {self.allocated_quantity} of req_item {self.requisition_item_id} -> po_item {self.po_item_id}"
