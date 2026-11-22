"""Command to transfer stock between warehouses atomically."""

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
    validate_batch_not_expired,
    validate_batch_requirement,
    validate_different_warehouses,
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
class TransferLineInput:
    item_id: UUID
    quantity: Decimal
    source_location_id: UUID | None = None
    destination_location_id: UUID | None = None
    batch_id: UUID | None = None


@dataclass(frozen=True)
class TransferStockInput:
    context: ExecutionContext
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    transaction_date: date
    lines: list[TransferLineInput]
    reference_document: str = ""
    notes: str = ""


@dataclass(frozen=True)
class TransferStockResult:
    transaction_id: UUID
    transaction_number: str
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    total_lines: int
    total_quantity_transferred: Decimal


@transaction.atomic
def execute(input_data: TransferStockInput) -> TransferStockResult:
    """Execute an immediate atomic transfer between two warehouses.

    Guarantees conservation of mass: for every line, an outward movement (-Q)
    at the source warehouse is balanced with an inward movement (+Q) at the destination.
    """
    ctx = input_data.context
    if ctx.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(ctx, "inventory:stock:transfer")

    if not input_data.lines:
        raise InventoryError("Transfer must include at least one item line.")

    validate_different_warehouses(
        str(input_data.source_warehouse_id),
        str(input_data.destination_warehouse_id),
    )

    source_wh = Warehouse.objects.filter(
        id=input_data.source_warehouse_id,
        organization_id=ctx.organization_id,
    ).first()
    if not source_wh:
        raise WarehouseNotFoundError(f"Source warehouse {input_data.source_warehouse_id} not found.")
    validate_warehouse_active(source_wh.is_active)

    dest_wh = Warehouse.objects.filter(
        id=input_data.destination_warehouse_id,
        organization_id=ctx.organization_id,
    ).first()
    if not dest_wh:
        raise WarehouseNotFoundError(f"Destination warehouse {input_data.destination_warehouse_id} not found.")
    validate_warehouse_active(dest_wh.is_active)

    txn_number = generate_document_number(ctx.organization_id, "TXN", StockTransaction)

    txn = StockTransaction.objects.create(
        organization_id=ctx.organization_id,
        transaction_number=txn_number,
        transaction_type=TransactionType.TRANSFER.value,
        status=TransactionStatus.POSTED.value,
        source_warehouse=source_wh,
        destination_warehouse=dest_wh,
        transaction_date=input_data.transaction_date,
        executed_by=ctx.actor_id,
        reference_document=input_data.reference_document,
        notes=input_data.notes,
    )

    posting_lines: list[LedgerPostingLine] = []
    total_quantity = Decimal("0.00")

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
            validate_batch_not_expired(
                item.track_expiry,
                batch.expiry_date,
                input_data.transaction_date,
            )

        source_loc: StorageLocation | None = None
        if line.source_location_id:
            source_loc = StorageLocation.objects.filter(
                id=line.source_location_id,
                warehouse=source_wh,
            ).first()
            if not source_loc:
                raise LocationNotFoundError(f"Source storage location {line.source_location_id} not found.")

        dest_loc: StorageLocation | None = None
        if line.destination_location_id:
            dest_loc = StorageLocation.objects.filter(
                id=line.destination_location_id,
                warehouse=dest_wh,
            ).first()
            if not dest_loc:
                raise LocationNotFoundError(f"Destination storage location {line.destination_location_id} not found.")

        # Outward entry at source warehouse (-Q)
        posting_lines.append(
            LedgerPostingLine(
                item=item,
                warehouse=source_wh,
                location=source_loc,
                batch=batch,
                quantity=-line.quantity,
                unit_cost=item.default_unit_cost,
            )
        )

        # Inward entry at destination warehouse (+Q)
        posting_lines.append(
            LedgerPostingLine(
                item=item,
                warehouse=dest_wh,
                location=dest_loc,
                batch=batch,
                quantity=line.quantity,
                unit_cost=item.default_unit_cost,
            )
        )

        total_quantity += line.quantity

    post_ledger_entries(txn, posting_lines)

    record_audit_event(
        actor_type=ctx.actor_type.value,
        actor_id=ctx.actor_id,
        actor_role=ctx.actor_role,
        organization_id=ctx.organization_id,
        action="inventory.stock.transferred",
        target_type="inventory.StockTransaction",
        target_id=txn.id,
        correlation_id=ctx.correlation_id,
        metadata={
            "transaction_number": txn.transaction_number,
            "source_warehouse_id": str(source_wh.id),
            "source_warehouse_code": source_wh.code,
            "destination_warehouse_id": str(dest_wh.id),
            "destination_warehouse_code": dest_wh.code,
            "total_lines": len(input_data.lines),
            "total_quantity": str(total_quantity),
        },
    )

    return TransferStockResult(
        transaction_id=txn.id,
        transaction_number=txn.transaction_number,
        source_warehouse_id=source_wh.id,
        destination_warehouse_id=dest_wh.id,
        total_lines=len(input_data.lines),
        total_quantity_transferred=total_quantity,
    )
