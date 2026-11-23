import uuid

from django.db import models

from abren_one.modules.inventory.domain.exceptions import (
    ImmutableStockTransactionError,
)
from abren_one.modules.inventory.domain.value_objects import (
    TransactionStatus,
    TransactionType,
)
from abren_one.modules.inventory.models.warehouse import Warehouse
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class StockTransaction(OrgOwnedMixin, TimestampMixin, models.Model):
    """Business document representing a stock movement event."""

    NUMBER_FIELD = "transaction_number"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_number = models.CharField(max_length=50, db_index=True)
    transaction_type = models.CharField(
        max_length=30,
        choices=[(t.value, t.value) for t in TransactionType],
    )
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in TransactionStatus],
        default=TransactionStatus.POSTED.value,
    )
    source_warehouse = models.ForeignKey(
        Warehouse,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="outward_transactions",
    )
    destination_warehouse = models.ForeignKey(
        Warehouse,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="inward_transactions",
    )
    transaction_date = models.DateField()
    executed_by = models.UUIDField(null=True, blank=True)
    reference_document = models.CharField(max_length=100, blank=True, default="")
    donor_name = models.CharField(max_length=255, blank=True, default="")
    purchase_order_id = models.UUIDField(null=True, blank=True, db_index=True)
    goods_receipt_id = models.UUIDField(null=True, blank=True, db_index=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "inventory_stock_transaction"
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"
        ordering = ["-transaction_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "transaction_number"],
                name="unique_transaction_number_per_org",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.transaction_number} ({self.transaction_type})"

    def save(self, *args, **kwargs) -> None:
        if not self._state.adding:
            orig = StockTransaction.objects.filter(pk=self.pk).values("status").first()
            if orig and orig["status"] == TransactionStatus.POSTED.value:
                raise ImmutableStockTransactionError("Posted stock transactions cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        if self.status == TransactionStatus.POSTED.value:
            raise ImmutableStockTransactionError("Posted stock transactions cannot be deleted.")
        super().delete(*args, **kwargs)
