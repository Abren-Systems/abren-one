import uuid

from django.db import models

from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class ItemBatch(OrgOwnedMixin, TimestampMixin, models.Model):
    """Specific lot and expiry identification for an inventory item."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.CASCADE,
        related_name="batches",
    )
    batch_number = models.CharField(max_length=100)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "inventory_item_batch"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["item", "batch_number"],
                name="unique_item_batch_number",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.item.item_code} (Lot: {self.batch_number})"
