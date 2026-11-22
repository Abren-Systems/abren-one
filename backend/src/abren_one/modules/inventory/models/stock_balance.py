from decimal import Decimal

from django.db import models

from abren_one.modules.inventory.models.item import Item
from abren_one.modules.inventory.models.item_batch import ItemBatch
from abren_one.modules.inventory.models.storage_location import StorageLocation
from abren_one.modules.inventory.models.warehouse import Warehouse
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class StockBalance(OrgOwnedMixin, TimestampMixin):
    """Current operational quantity projection by warehouse, location, item, and batch."""

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="balances",
    )
    location = models.ForeignKey(
        StorageLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="balances",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="balances",
    )
    batch = models.ForeignKey(
        ItemBatch,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="balances",
    )
    quantity_on_hand = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    quantity_reserved = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        db_table = "inventory_stock_balance"
        verbose_name = "Stock Balance"
        verbose_name_plural = "Stock Balances"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity_on_hand__gte=0),
                name="inventory_balance_qoh_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_reserved__gte=0),
                name="inventory_balance_qres_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_reserved__lte=models.F("quantity_on_hand")),
                name="inventory_balance_reserved_lte_on_hand",
            ),
            models.UniqueConstraint(
                fields=["organization", "warehouse", "item"],
                condition=models.Q(location__isnull=True, batch__isnull=True),
                name="unique_balance_no_loc_no_batch",
            ),
            models.UniqueConstraint(
                fields=["organization", "warehouse", "location", "item"],
                condition=models.Q(batch__isnull=True),
                name="unique_balance_loc_no_batch",
            ),
            models.UniqueConstraint(
                fields=["organization", "warehouse", "item", "batch"],
                condition=models.Q(location__isnull=True),
                name="unique_balance_no_loc_batch",
            ),
            models.UniqueConstraint(
                fields=["organization", "warehouse", "location", "item", "batch"],
                condition=models.Q(location__isnull=False, batch__isnull=False),
                name="unique_balance_loc_batch",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.item.name} @ {self.warehouse.code}: {self.quantity_on_hand} on hand"

    @property
    def available_quantity(self) -> Decimal:
        """Physical quantity available to promise or issue."""
        return Decimal(str(self.quantity_on_hand)) - Decimal(str(self.quantity_reserved))
