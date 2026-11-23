"""Command to receive stock from an accepted procurement Goods Receipt Note (GRN)."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import models, transaction

from abren_one.modules.inventory.application.balance_service import (
    LedgerPostingLine,
    post_ledger_entries,
)
from abren_one.modules.inventory.application.bridges.finance_gl import (
    post_purchase_receipt_gl,
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
    StockLedgerEntry,
    StockTransaction,
    StorageLocation,
    Warehouse,
)
from abren_one.modules.procurement.public import (
    GoodsReceiptNotFoundError,
    ProcurementError,
    get_grn_details,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ReceivePurchasedStockLineInput:
    po_item_id: UUID
    item_id: UUID
    quantity: Decimal
    unit_cost: Decimal | None = None
    location_id: UUID | None = None
    batch_id: UUID | None = None
    batch_number: str = ""
    expiry_date: date | None = None


@dataclass(frozen=True)
class ReceivePurchasedStockInput:
    context: ExecutionContext
    warehouse_id: UUID
    goods_receipt_id: UUID
    transaction_date: date
    lines: list[ReceivePurchasedStockLineInput]
    reference_document: str = ""
    notes: str = ""


@dataclass(frozen=True)
class ReceivePurchasedStockResult:
    transaction_id: UUID
    transaction_number: str
    goods_receipt_id: UUID
    goods_receipt_number: str
    purchase_order_id: UUID
    purchase_order_number: str
    total_lines: int
    total_quantity: Decimal
    destination_warehouse_id: UUID


@transaction.atomic
def execute(input_data: ReceivePurchasedStockInput) -> ReceivePurchasedStockResult:
    """Receive inspected and accepted goods from a Procurement GRN into a warehouse."""
    ctx = input_data.context
    if ctx.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(ctx, "inventory:stock:receive")

    if not input_data.lines:
        raise InventoryError("Receipt must include at least one item line.")

    # 1. Validate destination warehouse
    warehouse = Warehouse.objects.filter(
        id=input_data.warehouse_id,
        organization_id=ctx.organization_id,
    ).first()
    if not warehouse:
        raise WarehouseNotFoundError(f"Warehouse {input_data.warehouse_id} not found in this organization.")
    validate_warehouse_active(warehouse.is_active)

    # 2. Fetch and validate GRN from Procurement public contract
    try:
        grn = get_grn_details(ctx.organization_id, input_data.goods_receipt_id)
    except (GoodsReceiptNotFoundError, ProcurementError) as exc:
        raise InventoryError(f"Goods receipt note {input_data.goods_receipt_id} not found or inaccessible.") from exc

    if grn.receipt_type != "goods":
        raise InventoryError(f"Cannot receive '{grn.receipt_type}' receipts into inventory. Must be 'goods'.")

    grn_items_by_po_item = {item.po_item_id: item for item in grn.items}

    # 3. Guard against over-intake across transactions
    current_requested_totals: dict[UUID, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for line in input_data.lines:
        validate_positive_quantity(line.quantity)
        current_requested_totals[line.po_item_id] += line.quantity

    for po_item_id, requested_qty in current_requested_totals.items():
        grn_line = grn_items_by_po_item.get(po_item_id)
        if not grn_line:
            raise InventoryError(f"Purchase order item {po_item_id} is not part of goods receipt {grn.receipt_number}.")

        if not grn_line.is_inspected:
            raise InventoryError(f"Goods receipt item '{grn_line.description}' has not been inspected.")

        if grn_line.quantity_accepted <= Decimal("0.00"):
            raise InventoryError(
                f"Goods receipt item '{grn_line.description}' has no accepted quantity to receive into stock."
            )

        already_received = StockLedgerEntry.objects.filter(
            transaction__goods_receipt_id=grn.grn_id,
            po_item_id=po_item_id,
            quantity__gt=0,
        ).aggregate(total=models.Sum("quantity"))["total"] or Decimal("0.00")

        available_to_receive = grn_line.quantity_accepted - Decimal(str(already_received))
        if requested_qty > available_to_receive:
            raise InventoryError(
                f"Requested quantity {requested_qty} for '{grn_line.description}' exceeds remaining accepted "
                f"quantity {available_to_receive} (Accepted: {grn_line.quantity_accepted}, "
                f"Already received: {already_received})."
            )

    # 4. Generate sequential transaction document number
    txn_number = generate_document_number(ctx.organization_id, "TXN", StockTransaction)

    ref_doc = input_data.reference_document.strip() or grn.receipt_number

    txn = StockTransaction.objects.create(
        organization_id=ctx.organization_id,
        transaction_number=txn_number,
        transaction_type=TransactionType.RECEIPT_PURCHASE.value,
        status=TransactionStatus.POSTED.value,
        destination_warehouse=warehouse,
        transaction_date=input_data.transaction_date,
        executed_by=ctx.actor_id,
        reference_document=ref_doc,
        purchase_order_id=grn.purchase_order_id,
        goods_receipt_id=grn.grn_id,
        notes=input_data.notes,
    )

    posting_lines: list[LedgerPostingLine] = []
    total_quantity = Decimal("0.00")

    for line in input_data.lines:
        grn_line = grn_items_by_po_item[line.po_item_id]

        item = Item.objects.filter(
            id=line.item_id,
            organization_id=ctx.organization_id,
        ).first()
        if not item:
            raise ItemNotFoundError(f"Item {line.item_id} not found in this organization.")
        validate_item_active(item.is_active)

        # Batch handling
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
        elif line.batch_number.strip():
            batch_num = line.batch_number.strip()
            batch, _ = ItemBatch.objects.get_or_create(
                organization_id=ctx.organization_id,
                item=item,
                batch_number=batch_num,
                defaults={"expiry_date": line.expiry_date},
            )

        validate_batch_requirement(item.track_batches, batch is not None)

        # Location handling
        location: StorageLocation | None = None
        if line.location_id:
            location = StorageLocation.objects.filter(
                id=line.location_id,
                warehouse=warehouse,
            ).first()
            if not location:
                raise LocationNotFoundError(f"Storage location {line.location_id} not found in this warehouse.")

        unit_cost = line.unit_cost if line.unit_cost is not None else grn_line.unit_price

        posting_lines.append(
            LedgerPostingLine(
                item=item,
                warehouse=warehouse,
                location=location,
                batch=batch,
                quantity=line.quantity,
                unit_cost=unit_cost,
                po_item_id=line.po_item_id,
            )
        )
        total_quantity += line.quantity

    post_ledger_entries(txn, posting_lines)

    record_audit_event(
        actor_type=ctx.actor_type.value,
        actor_id=ctx.actor_id,
        actor_role=ctx.actor_role,
        organization_id=ctx.organization_id,
        action="inventory.stock.purchase_received",
        target_type="inventory.StockTransaction",
        target_id=txn.id,
        correlation_id=ctx.correlation_id,
        metadata={
            "transaction_number": txn.transaction_number,
            "goods_receipt_id": str(grn.grn_id),
            "goods_receipt_number": grn.receipt_number,
            "purchase_order_id": str(grn.purchase_order_id),
            "purchase_order_number": grn.purchase_order_number,
            "warehouse_id": str(warehouse.id),
            "warehouse_code": warehouse.code,
            "total_lines": len(input_data.lines),
            "total_quantity": str(total_quantity),
        },
    )

    # ── Cross-module GL bridge (ADR-006) ──────────────────────────────
    total_value = sum(
        line.quantity
        * (line.unit_cost if line.unit_cost is not None else grn_items_by_po_item[line.po_item_id].unit_price)
        for line in input_data.lines
    )
    if total_value > Decimal("0.00"):
        post_purchase_receipt_gl(
            organization_id=ctx.organization_id,
            transaction_number=txn.transaction_number,
            total_value=total_value,
            currency="USD",
            entry_date=input_data.transaction_date,
            goods_receipt_number=grn.receipt_number,
            purchase_order_number=grn.purchase_order_number,
        )

    return ReceivePurchasedStockResult(
        transaction_id=txn.id,
        transaction_number=txn.transaction_number,
        goods_receipt_id=grn.grn_id,
        goods_receipt_number=grn.receipt_number,
        purchase_order_id=grn.purchase_order_id,
        purchase_order_number=grn.purchase_order_number,
        total_lines=len(input_data.lines),
        total_quantity=total_quantity,
        destination_warehouse_id=warehouse.id,
    )
