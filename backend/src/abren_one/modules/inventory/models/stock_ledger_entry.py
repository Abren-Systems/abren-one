import uuid
from decimal import Decimal

from django.db import models

from abren_one.modules.inventory.domain.exceptions import (
    ImmutableStockTransactionError,
)
from abren_one.modules.inventory.models.item import Item
from abren_one.modules.inventory.models.item_batch import ItemBatch
from abren_one.modules.inventory.models.stock_transaction import StockTransaction
from abren_one.modules.inventory.models.storage_location import StorageLocation
from abren_one.modules.inventory.models.warehouse import Warehouse
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class StockLedgerEntry(OrgOwnedMixin, TimestampMixin, models.Model):
    """Immutable record of an individual item quantity movement."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        StockTransaction,
        on_delete=models.PROTECT,
        related_name="entries",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    batch = models.ForeignKey(
        ItemBatch,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    location = models.ForeignKey(
        StorageLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Signed quantity: positive for inward, negative for outward movement.",
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Informational acquisition cost per unit.",
    )
    program_id = models.UUIDField(null=True, blank=True, db_index=True)
    activity_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "inventory_stock_ledger_entry"
        verbose_name = "Stock Ledger Entry"
        verbose_name_plural = "Stock Ledger Entries"
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(quantity=0),
                name="inventory_ledger_quantity_nonzero",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.item.name} ({self.quantity:+f}) @ {self.warehouse.code}"

    def save(self, *args, **kwargs) -> None:
        if not self._state.adding:
            raise ImmutableStockTransactionError("Posted stock ledger entries cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        raise ImmutableStockTransactionError("Posted stock ledger entries cannot be deleted.")
