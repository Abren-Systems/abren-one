"""Command to record in-kind stock donations received at a warehouse."""

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
class DonationReceiptLineInput:
    item_id: UUID
    quantity: Decimal
    unit_cost: Decimal = Decimal("0.00")
    location_id: UUID | None = None
    batch_id: UUID | None = None


@dataclass(frozen=True)
class ReceiveDonationInput:
    context: ExecutionContext
    warehouse_id: UUID
    donor_name: str
    transaction_date: date
    lines: list[DonationReceiptLineInput]
    reference_document: str = ""
    notes: str = ""


@dataclass(frozen=True)
class DonationReceiptResult:
    transaction_id: UUID
    transaction_number: str
    donor_name: str
    total_lines: int
    total_quantity: Decimal
    destination_warehouse_id: UUID


@transaction.atomic
def execute(input_data: ReceiveDonationInput) -> DonationReceiptResult:
    """Record an in-kind donation receipt into a warehouse."""
    ctx = input_data.context
    if ctx.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(ctx, "inventory:stock:receive")

    if not input_data.lines:
        raise InventoryError("Donation receipt must include at least one item line.")

    if not input_data.donor_name.strip():
        raise InventoryError("Donor name is required for in-kind donation receipts.")

    # Validate warehouse
    warehouse = Warehouse.objects.filter(
        id=input_data.warehouse_id,
        organization_id=ctx.organization_id,
    ).first()
    if not warehouse:
        raise WarehouseNotFoundError(f"Warehouse {input_data.warehouse_id} not found in this organization.")
    validate_warehouse_active(warehouse.is_active)

    # Generate transaction document number
    txn_number = generate_document_number(ctx.organization_id, "TXN", StockTransaction)

    txn = StockTransaction.objects.create(
        organization_id=ctx.organization_id,
        transaction_number=txn_number,
        transaction_type=TransactionType.RECEIPT_DONATION.value,
        status=TransactionStatus.POSTED.value,
        destination_warehouse=warehouse,
        transaction_date=input_data.transaction_date,
        executed_by=ctx.actor_id,
        reference_document=input_data.reference_document,
        donor_name=input_data.donor_name.strip(),
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

        location: StorageLocation | None = None
        if line.location_id:
            location = StorageLocation.objects.filter(
                id=line.location_id,
                warehouse=warehouse,
            ).first()
            if not location:
                raise LocationNotFoundError(f"Storage location {line.location_id} not found in this warehouse.")

        posting_lines.append(
            LedgerPostingLine(
                item=item,
                warehouse=warehouse,
                location=location,
                batch=batch,
                quantity=line.quantity,
                unit_cost=line.unit_cost,
            )
        )
        total_quantity += line.quantity

    post_ledger_entries(txn, posting_lines)

    record_audit_event(
        actor_type=ctx.actor_type.value,
        actor_id=ctx.actor_id,
        actor_role=ctx.actor_role,
        organization_id=ctx.organization_id,
        action="inventory.stock.donation_received",
        target_type="inventory.StockTransaction",
        target_id=txn.id,
        correlation_id=ctx.correlation_id,
        metadata={
            "transaction_number": txn.transaction_number,
            "donor_name": txn.donor_name,
            "warehouse_id": str(warehouse.id),
            "warehouse_code": warehouse.code,
            "total_lines": len(input_data.lines),
            "total_quantity": str(total_quantity),
        },
    )

    return DonationReceiptResult(
        transaction_id=txn.id,
        transaction_number=txn.transaction_number,
        donor_name=txn.donor_name,
        total_lines=len(input_data.lines),
        total_quantity=total_quantity,
        destination_warehouse_id=warehouse.id,
    )
