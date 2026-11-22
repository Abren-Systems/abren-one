from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    ItemNotFoundError,
)
from abren_one.modules.inventory.models import Item
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class BatchSummaryDto:
    id: UUID
    batch_number: str
    manufacture_date: date | None
    expiry_date: date | None


@dataclass(frozen=True)
class ItemDetailResult:
    id: UUID
    item_code: str
    name: str
    description: str
    category_id: UUID
    category_name: str
    category_code: str
    unit_of_measure: str
    item_type: str
    track_batches: bool
    track_expiry: bool
    reorder_threshold: Decimal
    default_unit_cost: Decimal
    is_active: bool
    batches: list[BatchSummaryDto]


def execute(context: ExecutionContext, item_id: UUID) -> ItemDetailResult:
    """Retrieve detailed specification and registered batches for an inventory item."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    try:
        item = (
            Item.objects.filter(
                id=item_id,
                organization_id=context.organization_id,
            )
            .select_related("category")
            .prefetch_related("batches")
            .get()
        )
    except Item.DoesNotExist as exc:
        raise ItemNotFoundError("Item not found in this organization.") from exc

    batches_dto = [
        BatchSummaryDto(
            id=b.id,
            batch_number=b.batch_number,
            manufacture_date=b.manufacture_date,
            expiry_date=b.expiry_date,
        )
        for b in item.batches.all().order_by("expiry_date", "batch_number")
    ]

    return ItemDetailResult(
        id=item.id,
        item_code=item.item_code,
        name=item.name,
        description=item.description,
        category_id=item.category_id,
        category_name=item.category.name,
        category_code=item.category.code,
        unit_of_measure=item.unit_of_measure,
        item_type=item.item_type,
        track_batches=item.track_batches,
        track_expiry=item.track_expiry,
        reorder_threshold=item.reorder_threshold,
        default_unit_cost=item.default_unit_cost,
        is_active=item.is_active,
        batches=batches_dto,
    )
