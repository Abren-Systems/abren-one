import uuid

from django.db import models

from abren_one.modules.procurement.domain.value_objects import ReceiptType
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class GoodsReceiptNote(OrgOwnedMixin, TimestampMixin, models.Model):
    """Evidence of physical delivery or service completion against a purchase order."""

    NUMBER_FIELD = "receipt_number"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt_number = models.CharField(max_length=100)
    purchase_order = models.ForeignKey(
        "procurement.PurchaseOrder",
        on_delete=models.PROTECT,
        related_name="goods_receipts",
    )
    receipt_type = models.CharField(
        max_length=30,
        choices=[(t.value, t.name) for t in ReceiptType],
        default=ReceiptType.GOODS.value,
    )
    received_date = models.DateField()
    received_by = models.UUIDField()
    inspection_notes = models.TextField(blank=True, default="")
    is_correction = models.BooleanField(default=False)
    corrects = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="corrections",
    )

    class Meta:
        db_table = "procurement_goods_receipt_note"
        ordering = ["-received_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "receipt_number"],
                name="unique_receipt_number_per_org",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.receipt_number} ({self.receipt_type})"

    @property
    def is_fully_inspected(self) -> bool:
        return self.items.exists() and not self.items.filter(is_inspected=False).exists()

    @property
    def has_rejections(self) -> bool:
        return self.items.filter(quantity_rejected__gt=0).exists()


class GoodsReceiptItem(TimestampMixin, models.Model):
    """Line-level goods receipt with quantity reconciliation and inspection state."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goods_receipt = models.ForeignKey(
        "procurement.GoodsReceiptNote",
        on_delete=models.CASCADE,
        related_name="items",
    )
    po_item = models.ForeignKey(
        "procurement.PurchaseOrderItem",
        on_delete=models.PROTECT,
        related_name="receipt_items",
    )
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_rejected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_inspected = models.BooleanField(default=False)
    rejection_reason = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        db_table = "procurement_goods_receipt_item"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity_received__gte=0),
                name="grn_item_received_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_accepted__gte=0),
                name="grn_item_accepted_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_rejected__gte=0),
                name="grn_item_rejected_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"GRN Item {self.id}: received={self.quantity_received}, "
            f"accepted={self.quantity_accepted}, rejected={self.quantity_rejected}"
        )
