"""Command to record authorized stock write-offs (damage, expiry, loss)."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.application.balance_service import (
    LedgerPostingLine,
    post_ledger_entries,
)
from abren_one.modules.inventory.application.bridges.finance_gl import (
    post_write_off_gl,
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
    validate_batch_not_expired,
    validate_batch_requirement,
    validate_item_active,
    validate_positive_quantity,
    validate_warehouse_active,
)
from abren_one.modules.inventory.domain.value_objects import (
    TransactionStatus,
    TransactionType,
)
from abren_one.modules.inventory.models import (
    Item,
    ItemBatch,
    StockTransaction,
    StorageLocation,
    Warehouse,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class WriteOffLineInput:
    item_id: UUID
    quantity: Decimal
    reason: str
    location_id: UUID | None = None
    batch_id: UUID | None = None


@dataclass(frozen=True)
class WriteOffStockInput:
    context: ExecutionContext
    warehouse_id: UUID
    transaction_date: date
    approval_reference: str
    justification: str
    lines: list[WriteOffLineInput]


@dataclass(frozen=True)
class WriteOffStockResult:
    transaction_id: UUID
    transaction_number: str
    warehouse_id: UUID
    approval_reference: str
    total_lines: int
    total_quantity_written_off: Decimal


@transaction.atomic
def execute(input_data: WriteOffStockInput) -> WriteOffStockResult:
    """Execute an authorized disposal or write-off of damaged, expired, or lost stock.

    Restricted to Owner/Admin via inventory:stock:adjust. Bypasses expiry checks
    since disposing of expired inventory is explicitly permitted.
    """
    ctx = input_data.context
    if ctx.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(ctx, "inventory:stock:adjust")

    if not input_data.lines:
        raise InventoryError("Write-off must include at least one item line.")

    if not input_data.approval_reference.strip():
        raise InventoryError("Formal approval reference is required for write-off disposal.")

    if not input_data.justification.strip():
        raise InventoryError("Written justification is required for write-off disposal.")

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
        transaction_type=TransactionType.WRITE_OFF_DISPOSAL.value,
        status=TransactionStatus.POSTED.value,
        source_warehouse=warehouse,
        transaction_date=input_data.transaction_date,
        executed_by=ctx.actor_id,
        reference_document=input_data.approval_reference.strip(),
        notes=input_data.justification.strip(),
    )

    posting_lines: list[LedgerPostingLine] = []
    total_quantity = Decimal("0.00")
    total_value = Decimal("0.00")  # Track total value for GL bridge

    for line in input_data.lines:
        validate_positive_quantity(line.quantity)

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

        if batch:
            # Explicitly authorized disposal allows expired batches to be written off
            validate_batch_not_expired(
                item.track_expiry,
                batch.expiry_date,
                input_data.transaction_date,
                is_disposal=True,
            )

        location: StorageLocation | None = None
        if line.location_id:
            location = StorageLocation.objects.filter(
                id=line.location_id,
                warehouse=warehouse,
            ).first()
            if not location:
                raise LocationNotFoundError(f"Storage location {line.location_id} not found.")

        posting_lines.append(
            LedgerPostingLine(
                item=item,
                warehouse=warehouse,
                location=location,
                batch=batch,
                quantity=-line.quantity,  # Outward removal
                unit_cost=item.default_unit_cost,
            )
        )
        total_quantity += line.quantity
        total_value += line.quantity * item.default_unit_cost

    post_ledger_entries(txn, posting_lines)

    record_audit_event(
        actor_type=ctx.actor_type.value,
        actor_id=ctx.actor_id,
        actor_role=ctx.actor_role,
        organization_id=ctx.organization_id,
        action="inventory.stock.written_off",
        target_type="inventory.StockTransaction",
        target_id=txn.id,
        correlation_id=ctx.correlation_id,
        metadata={
            "transaction_number": txn.transaction_number,
            "warehouse_id": str(warehouse.id),
            "warehouse_code": warehouse.code,
            "approval_reference": input_data.approval_reference,
            "justification": input_data.justification,
            "total_lines": len(input_data.lines),
            "total_quantity": str(total_quantity),
        },
    )

    # ── Cross-module GL bridge (ADR-006) ──────────────────────────────
    if total_value > Decimal("0.00"):
        post_write_off_gl(
            organization_id=ctx.organization_id,
            transaction_number=txn.transaction_number,
            total_value=total_value,
            currency="USD",
            entry_date=input_data.transaction_date,
            approval_reference=input_data.approval_reference,
        )

    return WriteOffStockResult(
        transaction_id=txn.id,
        transaction_number=txn.transaction_number,
        warehouse_id=warehouse.id,
        approval_reference=input_data.approval_reference,
        total_lines=len(input_data.lines),
        total_quantity_written_off=total_quantity,
    )
