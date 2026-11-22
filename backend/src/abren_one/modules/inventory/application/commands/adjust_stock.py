"""Command to reconcile inventory based on verified physical cycle counts."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.application.balance_service import (
    LedgerPostingLine,
    post_ledger_entries,
)
from abren_one.modules.inventory.application.number_generation import (
    generate_document_number,
)
from abren_one.modules.inventory.domain.exceptions import (
    BatchNotFoundError,
    InventoryError,
    ItemNotFoundError,
    LocationNotFoundError,
    OrganizationMismatchError,
    WarehouseNotFoundError,
)
from abren_one.modules.inventory.domain.policies import (
    validate_batch_requirement,
    validate_item_active,
    validate_non_negative,
    validate_warehouse_active,
)
from abren_one.modules.inventory.domain.value_objects import (
    TransactionStatus,
    TransactionType,
)
from abren_one.modules.inventory.models import (
    Item,
    ItemBatch,
    StockBalance,
    StockTransaction,
    StorageLocation,
    Warehouse,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class AdjustmentLineInput:
    item_id: UUID
    actual_quantity_counted: Decimal
    location_id: UUID | None = None
    batch_id: UUID | None = None
    reason: str = ""


@dataclass(frozen=True)
class AdjustStockInput:
    context: ExecutionContext
    warehouse_id: UUID
    transaction_date: date
    justification: str
    lines: list[AdjustmentLineInput]
    reference_document: str = ""


@dataclass(frozen=True)
class AdjustStockResult:
    transaction_id: UUID
    transaction_number: str
    warehouse_id: UUID
    lines_adjusted: int
    net_quantity_delta: Decimal


@transaction.atomic
def execute(input_data: AdjustStockInput) -> AdjustStockResult:
    """Reconcile inventory quantity projections against physical count observations.

    Restricted to Owner/Admin via inventory:stock:adjust. Computes delta (actual - current)
    and emits compensating signed ledger entries (+surplus / -shortage).
    """
    ctx = input_data.context
    if ctx.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(ctx, "inventory:stock:adjust")

    if not input_data.justification.strip():
        raise InventoryError("Written justification is required for cycle count adjustments.")

    if not input_data.lines:
        raise InventoryError("Adjustment must include at least one count line.")

    warehouse = Warehouse.objects.filter(
        id=input_data.warehouse_id,
        organization_id=ctx.organization_id,
    ).first()
    if not warehouse:
        raise WarehouseNotFoundError(f"Warehouse {input_data.warehouse_id} not found.")
    validate_warehouse_active(warehouse.is_active)

    txn_number = generate_document_number(ctx.organization_id, "TXN", StockTransaction)
    txn = StockTransaction.objects.create(
        organization_id=ctx.organization_id,
        transaction_number=txn_number,
        transaction_type=TransactionType.ADJUSTMENT_COUNT.value,
        status=TransactionStatus.POSTED.value,
        destination_warehouse=warehouse,
        transaction_date=input_data.transaction_date,
        executed_by=ctx.actor_id,
        reference_document=input_data.reference_document,
        notes=input_data.justification.strip(),
    )

    posting_lines: list[LedgerPostingLine] = []
    net_delta = Decimal("0.00")

    for line in input_data.lines:
        validate_non_negative(line.actual_quantity_counted)

        item = Item.objects.filter(
            id=line.item_id,
            organization_id=ctx.organization_id,
        ).first()
        if not item:
            raise ItemNotFoundError(f"Item {line.item_id} not found in this organization.")
        validate_item_active(item.is_active)

        batch: ItemBatch | None = None
        if line.batch_id:
            batch = ItemBatch.objects.filter(
                id=line.batch_id,
                organization_id=ctx.organization_id,
            ).first()
            if not batch:
                raise BatchNotFoundError(f"Batch {line.batch_id} not found.")
            if batch.item_id != item.id:
                raise OrganizationMismatchError(f"Batch {line.batch_id} does not belong to item {item.name}.")
        validate_batch_requirement(item.track_batches, batch is not None)

        location: StorageLocation | None = None
        if line.location_id:
            location = StorageLocation.objects.filter(
                id=line.location_id,
                warehouse=warehouse,
            ).first()
            if not location:
                raise LocationNotFoundError(f"Storage location {line.location_id} not found.")

        # Determine current on-hand quantity
        current_balance = StockBalance.objects.filter(
            organization_id=ctx.organization_id,
            warehouse=warehouse,
            location=location,
            item=item,
            batch=batch,
        ).first()

        current_qoh = current_balance.quantity_on_hand if current_balance else Decimal("0.00")
        delta = line.actual_quantity_counted - current_qoh

        if delta == Decimal("0.00"):
            continue  # Exact match, no adjustment entry needed

        posting_lines.append(
            LedgerPostingLine(
                item=item,
                warehouse=warehouse,
                location=location,
                batch=batch,
                quantity=delta,  # Signed delta (+surplus, -shortage)
                unit_cost=item.default_unit_cost,
            )
        )
        net_delta += delta

    if not posting_lines:
        raise InventoryError("All counted quantities match current balances; no discrepancies to adjust.")

    post_ledger_entries(txn, posting_lines)

    record_audit_event(
        actor_type=ctx.actor_type.value,
        actor_id=ctx.actor_id,
        actor_role=ctx.actor_role,
        organization_id=ctx.organization_id,
        action="inventory.stock.adjusted",
        target_type="inventory.StockTransaction",
        target_id=txn.id,
        correlation_id=ctx.correlation_id,
        metadata={
            "transaction_number": txn.transaction_number,
            "warehouse_id": str(warehouse.id),
            "warehouse_code": warehouse.code,
            "justification": input_data.justification,
            "lines_adjusted": len(posting_lines),
            "net_quantity_delta": str(net_delta),
        },
    )

    return AdjustStockResult(
        transaction_id=txn.id,
        transaction_number=txn.transaction_number,
        warehouse_id=warehouse.id,
        lines_adjusted=len(posting_lines),
        net_quantity_delta=net_delta,
    )
