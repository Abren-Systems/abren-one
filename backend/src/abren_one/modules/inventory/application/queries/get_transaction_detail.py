"""Query to get detailed information about a stock transaction."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    TransactionNotFoundError,
)
from abren_one.modules.inventory.models import StockTransaction
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class TransactionEntryLineResult:
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
    batch_id: UUID | None
    batch_number: str | None
    quantity: Decimal
    unit_cost: Decimal
    program_id: UUID | None
    activity_id: UUID | None


@dataclass(frozen=True)
class StockTransactionDetailResult:
    id: UUID
    transaction_number: str
    transaction_type: str
    status: str
    transaction_date: date
    source_warehouse_id: UUID | None
    source_warehouse_name: str | None
    destination_warehouse_id: UUID | None
    destination_warehouse_name: str | None
    executed_by: UUID | None
    reference_document: str
    donor_name: str
    notes: str
    entries: list[TransactionEntryLineResult]


def execute(
    context: ExecutionContext,
    transaction_id: UUID,
) -> StockTransactionDetailResult:
    """Retrieve full details of a single stock transaction."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(context, "inventory:stock:view")

    txn = (
        StockTransaction.objects.filter(
            id=transaction_id,
            organization_id=context.organization_id,
        )
        .select_related("source_warehouse", "destination_warehouse")
        .prefetch_related(
            "entries__item",
            "entries__warehouse",
            "entries__location",
            "entries__batch",
        )
        .first()
    )

    if not txn:
        raise TransactionNotFoundError(f"Transaction {transaction_id} not found in this organization.")

    entry_results = [
        TransactionEntryLineResult(
            id=e.id,
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
        for e in txn.entries.all()
    ]

    return StockTransactionDetailResult(
        id=txn.id,
        transaction_number=txn.transaction_number,
        transaction_type=txn.transaction_type,
        status=txn.status,
        transaction_date=txn.transaction_date,
        source_warehouse_id=txn.source_warehouse.id if txn.source_warehouse else None,
        source_warehouse_name=txn.source_warehouse.name if txn.source_warehouse else None,
        destination_warehouse_id=txn.destination_warehouse.id if txn.destination_warehouse else None,
        destination_warehouse_name=txn.destination_warehouse.name if txn.destination_warehouse else None,
        executed_by=txn.executed_by,
        reference_document=txn.reference_document,
        donor_name=txn.donor_name,
        notes=txn.notes,
        entries=entry_results,
    )
