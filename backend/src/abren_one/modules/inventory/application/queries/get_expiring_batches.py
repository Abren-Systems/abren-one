"""Query to retrieve item batches approaching expiry with active stock on hand."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from django.utils import timezone

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import StockBalance
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ExpiringBatchAlertResult:
    batch_id: UUID
    batch_number: str
    item_id: UUID
    item_code: str
    item_name: str
    warehouse_id: UUID
    warehouse_name: str
    warehouse_code: str
    expiry_date: date
    days_until_expiry: int
    quantity_on_hand: Decimal
    is_already_expired: bool


def execute(
    context: ExecutionContext,
    days_ahead: int = 90,
    warehouse_id: UUID | None = None,
) -> list[ExpiringBatchAlertResult]:
    """Retrieve all on-hand stock batches expiring within the specified days window."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(context, "inventory:stock:view")

    today = timezone.now().date()
    cutoff_date = today + timedelta(days=days_ahead)

    qs = (
        StockBalance.objects.filter(
            organization_id=context.organization_id,
            batch__isnull=False,
            batch__expiry_date__isnull=False,
            batch__expiry_date__lte=cutoff_date,
            quantity_on_hand__gt=Decimal("0.00"),
        )
        .select_related("batch", "item", "warehouse")
        .order_by("batch__expiry_date")
    )

    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)

    results: list[ExpiringBatchAlertResult] = []
    for b in qs:
        batch = b.batch
        if not batch or not batch.expiry_date:
            continue

        days_remaining = (batch.expiry_date - today).days
        results.append(
            ExpiringBatchAlertResult(
                batch_id=batch.id,
                batch_number=batch.batch_number,
                item_id=b.item.id,
                item_code=b.item.item_code,
                item_name=b.item.name,
                warehouse_id=b.warehouse.id,
                warehouse_name=b.warehouse.name,
                warehouse_code=b.warehouse.code,
                expiry_date=batch.expiry_date,
                days_until_expiry=days_remaining,
                quantity_on_hand=b.quantity_on_hand,
                is_already_expired=days_remaining < 0,
            )
        )

    return results
