"""Query to retrieve stock ledger entries."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import StockLedgerEntry
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class StockLedgerEntryResult:
    id: UUID
    transaction_id: UUID
    transaction_number: str
    transaction_type: str
    transaction_date: date
    item_id: UUID
    item_code: str
    item_name: str
    unit_of_measure: str
    warehouse_id: UUID
    warehouse_name: str
    warehouse_code: str
    location_id: UUID | None
    location_name: str | None
    batch_id: UUID | None
    batch_number: str | None
    quantity: Decimal
    unit_cost: Decimal
    program_id: UUID | None
    activity_id: UUID | None


def execute(
    context: ExecutionContext,
    warehouse_id: UUID | None = None,
    item_id: UUID | None = None,
    transaction_id: UUID | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[StockLedgerEntryResult]:
    """Retrieve chronological stock ledger movements with bounded pagination."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(context, "inventory:stock:view")

    qs = (
        StockLedgerEntry.objects.filter(organization_id=context.organization_id)
        .select_related("transaction", "item", "warehouse", "location", "batch")
        .order_by("-transaction__transaction_date", "-created_at")
    )

    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)
    if item_id:
        qs = qs.filter(item_id=item_id)
    if transaction_id:
        qs = qs.filter(transaction_id=transaction_id)
    if from_date:
        qs = qs.filter(transaction__transaction_date__gte=from_date)
    if to_date:
        qs = qs.filter(transaction__transaction_date__lte=to_date)

    bounded_limit = min(max(1, limit), 200)
    entries = qs[offset : offset + bounded_limit]

    return [
        StockLedgerEntryResult(
            id=e.id,
            transaction_id=e.transaction.id,
            transaction_number=e.transaction.transaction_number,
            transaction_type=e.transaction.transaction_type,
            transaction_date=e.transaction.transaction_date,
            item_id=e.item.id,
            item_code=e.item.item_code,
            item_name=e.item.name,
            unit_of_measure=e.item.unit_of_measure,
            warehouse_id=e.warehouse.id,
            warehouse_name=e.warehouse.name,
            warehouse_code=e.warehouse.code,
            location_id=e.location.id if e.location else None,
            location_name=e.location.name if e.location else None,
            batch_id=e.batch.id if e.batch else None,
            batch_number=e.batch.batch_number if e.batch else None,
            quantity=e.quantity,
            unit_cost=e.unit_cost,
            program_id=e.program_id,
            activity_id=e.activity_id,
        )
        for e in entries
    ]
