from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import Item
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ItemSummaryResult:
    id: UUID
    item_code: str
    name: str
    category_id: UUID
    category_name: str
    unit_of_measure: str
    item_type: str
    track_batches: bool
    track_expiry: bool
    reorder_threshold: Decimal
    default_unit_cost: Decimal
    is_active: bool


def execute(
    context: ExecutionContext,
    category_id: UUID | None = None,
    item_type: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[ItemSummaryResult]:
    """List stock-tracked items for the active organization with bounded pagination."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    qs = Item.objects.filter(organization_id=context.organization_id).select_related("category").order_by("item_code")

    if category_id is not None:
        qs = qs.filter(category_id=category_id)
    if item_type:
        qs = qs.filter(item_type=item_type)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        search_term = search.strip()
        qs = qs.filter(item_code__icontains=search_term) | qs.filter(name__icontains=search_term)

    return [
        ItemSummaryResult(
            id=item.id,
            item_code=item.item_code,
            name=item.name,
            category_id=item.category_id,
            category_name=item.category.name,
            unit_of_measure=item.unit_of_measure,
            item_type=item.item_type,
            track_batches=item.track_batches,
            track_expiry=item.track_expiry,
            reorder_threshold=item.reorder_threshold,
            default_unit_cost=item.default_unit_cost,
            is_active=item.is_active,
        )
        for item in qs[offset : offset + limit]
    ]
