"""Query to list stock balances with optional filtering."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db.models import F

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import StockBalance
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class StockBalanceItemResult:
    id: UUID
    item_id: UUID
    item_code: str
    item_name: str
    unit_of_measure: str
    warehouse_id: UUID
    warehouse_name: str
    warehouse_code: str
    location_id: UUID | None
    location_name: str | None
    location_code: str | None
    batch_id: UUID | None
    batch_number: str | None
    expiry_date: date | None
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    available_quantity: Decimal
    reorder_threshold: Decimal
    is_low_stock: bool


def execute(
    context: ExecutionContext,
    warehouse_id: UUID | None = None,
    item_id: UUID | None = None,
    low_stock_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[StockBalanceItemResult]:
    """Retrieve current operational stock balances with bounded pagination."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(context, "inventory:stock:view")

    qs = (
        StockBalance.objects.filter(organization_id=context.organization_id)
        .select_related("item", "warehouse", "location", "batch")
        .order_by("warehouse__name", "item__name")
    )

    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)
    if item_id:
        qs = qs.filter(item_id=item_id)
    if low_stock_only:
        # Stock is low if available <= reorder_threshold and reorder_threshold > 0
        qs = qs.filter(
            quantity_on_hand__lte=F("item__reorder_threshold"),
            item__reorder_threshold__gt=0,
        )

    bounded_limit = min(max(1, limit), 200)
    balances = qs[offset : offset + bounded_limit]

    return [
        StockBalanceItemResult(
            id=b.id,
            item_id=b.item.id,
            item_code=b.item.item_code,
            item_name=b.item.name,
            unit_of_measure=b.item.unit_of_measure,
            warehouse_id=b.warehouse.id,
            warehouse_name=b.warehouse.name,
            warehouse_code=b.warehouse.code,
            location_id=b.location.id if b.location else None,
            location_name=b.location.name if b.location else None,
            location_code=b.location.code if b.location else None,
            batch_id=b.batch.id if b.batch else None,
            batch_number=b.batch.batch_number if b.batch else None,
            expiry_date=b.batch.expiry_date if b.batch else None,
            quantity_on_hand=b.quantity_on_hand,
            quantity_reserved=b.quantity_reserved,
            available_quantity=b.available_quantity,
            reorder_threshold=b.item.reorder_threshold,
            is_low_stock=(b.item.reorder_threshold > 0 and b.available_quantity <= b.item.reorder_threshold),
        )
        for b in balances
    ]
