import uuid
from decimal import Decimal

from django.db import models

from abren_one.modules.inventory.domain.value_objects import ItemType
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Item(OrgOwnedMixin, TimestampMixin, models.Model):
    """Master definition of a stock-tracked good or supply."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        "inventory.ItemCategory",
        on_delete=models.PROTECT,
        related_name="items",
    )
    item_code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    unit_of_measure = models.CharField(max_length=50, default="each")
    item_type = models.CharField(
        max_length=30,
        choices=[(t.value, t.name) for t in ItemType],
        default=ItemType.CONSUMABLE.value,
        db_index=True,
    )
    track_batches = models.BooleanField(default=False)
    track_expiry = models.BooleanField(default=False)
    reorder_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    default_unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "inventory_item"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "item_code"],
                name="unique_item_code_per_org",
            ),
            models.CheckConstraint(
                condition=models.Q(reorder_threshold__gte=0),
                name="item_reorder_threshold_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(default_unit_cost__gte=0),
                name="item_default_unit_cost_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.item_code} - {self.name}"
