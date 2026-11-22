import uuid

from django.db import models

from abren_one.platform.common.models import TimestampMixin


class StorageLocation(TimestampMixin, models.Model):
    """Internal storage zone, aisle, shelf, or bin within a warehouse."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="locations",
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "inventory_storage_location"
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "code"],
                name="unique_storage_location_code_per_warehouse",
            )
        ]

    def __str__(self) -> str:
        return f"{self.warehouse.code} - {self.name} ({self.code})"
