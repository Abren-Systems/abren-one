"""Query to retrieve stock items that are at or below their reorder threshold."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db.models import F

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import StockBalance
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ReorderAlertResult:
    item_id: UUID
    item_code: str
    item_name: str
    unit_of_measure: str
    warehouse_id: UUID
    warehouse_name: str
    warehouse_code: str
    quantity_on_hand: Decimal
    available_quantity: Decimal
    reorder_threshold: Decimal
    shortage_quantity: Decimal


def execute(
    context: ExecutionContext,
    warehouse_id: UUID | None = None,
) -> list[ReorderAlertResult]:
    """Retrieve all stock balance locations that are at or below reorder threshold."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(context, "inventory:stock:view")

    qs = (
        StockBalance.objects.filter(
            organization_id=context.organization_id,
            item__reorder_threshold__gt=Decimal("0.00"),
            item__is_active=True,
            quantity_on_hand__lte=F("item__reorder_threshold"),
        )
        .select_related("item", "warehouse")
        .order_by("warehouse__name", "item__name")
    )

    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)

    results: list[ReorderAlertResult] = []
    for b in qs:
        shortage = b.item.reorder_threshold - b.available_quantity
        results.append(
            ReorderAlertResult(
                item_id=b.item.id,
                item_code=b.item.item_code,
                item_name=b.item.name,
                unit_of_measure=b.item.unit_of_measure,
                warehouse_id=b.warehouse.id,
                warehouse_name=b.warehouse.name,
                warehouse_code=b.warehouse.code,
                quantity_on_hand=b.quantity_on_hand,
                available_quantity=b.available_quantity,
                reorder_threshold=b.item.reorder_threshold,
                shortage_quantity=max(Decimal("0.00"), shortage),
            )
        )

    return results
