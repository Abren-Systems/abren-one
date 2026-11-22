"""Query to check stock availability for an item across warehouses."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db.models import Sum

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    ItemNotFoundError,
)
from abren_one.modules.inventory.models import Item, StockBalance


@dataclass(frozen=True)
class ItemAvailabilityResult:
    item_id: UUID
    item_code: str
    item_name: str
    unit_of_measure: str
    total_on_hand: Decimal
    total_reserved: Decimal
    total_available: Decimal
    is_available: bool


def execute(
    organization_id: UUID,
    item_id: UUID,
    warehouse_id: UUID | None = None,
) -> ItemAvailabilityResult:
    """Check stock availability for an item within an organization.

    Public contract query for external modules (Procurement, Programs, Beneficiaries).
    """
    if organization_id is None:
        raise InventoryError("Organization ID is required.")

    item = Item.objects.filter(id=item_id, organization_id=organization_id).first()
    if not item:
        raise ItemNotFoundError(f"Item {item_id} not found in this organization.")

    qs = StockBalance.objects.filter(
        organization_id=organization_id,
        item=item,
    )
    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)

    aggregates = qs.aggregate(
        on_hand=Sum("quantity_on_hand"),
        reserved=Sum("quantity_reserved"),
    )

    total_on_hand = aggregates["on_hand"] or Decimal("0.00")
    total_reserved = aggregates["reserved"] or Decimal("0.00")
    total_available = total_on_hand - total_reserved

    return ItemAvailabilityResult(
        item_id=item.id,
        item_code=item.item_code,
        item_name=item.name,
        unit_of_measure=item.unit_of_measure,
        total_on_hand=total_on_hand,
        total_reserved=total_reserved,
        total_available=total_available,
        is_available=total_available > Decimal("0.00") and item.is_active,
    )
