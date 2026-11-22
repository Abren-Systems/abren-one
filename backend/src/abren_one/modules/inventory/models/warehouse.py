import uuid

from django.db import models

from abren_one.modules.inventory.domain.value_objects import WarehouseType
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Warehouse(OrgOwnedMixin, TimestampMixin, models.Model):
    """Physical stock-holding facility, depot, dispensary, or storage room."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch_id = models.UUIDField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    warehouse_type = models.CharField(
        max_length=30,
        choices=[(t.value, t.name) for t in WarehouseType],
        default=WarehouseType.REGIONAL_DEPOT.value,
        db_index=True,
    )
    custodian_id = models.UUIDField(null=True, blank=True)
    address = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "inventory_warehouse"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_warehouse_code_per_org",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
