from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.public import get_organization
from abren_one.modules.procurement.application.number_generation import (
    generate_document_number,
)
from abren_one.modules.procurement.domain.exceptions import (
    GoodsReceiptNotFoundError,
    OrganizationMismatchError,
    ProcurementError,
    PurchaseOrderNotFoundError,
)
from abren_one.modules.procurement.domain.policies import validate_receipt_quantity
from abren_one.modules.procurement.domain.value_objects import (
    PurchaseOrderStatus,
    ReceiptType,
)
from abren_one.modules.procurement.models import (
    GoodsReceiptItem,
    GoodsReceiptNote,
    PurchaseOrder,
    PurchaseOrderItem,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RecordReceiptItemInput:
    po_item_id: UUID
    quantity_received: Decimal


@dataclass(frozen=True)
class RecordGoodsReceiptInput:
    context: ExecutionContext
    purchase_order_id: UUID
    received_date: date
    receipt_type: str = ReceiptType.GOODS.value
    inspection_notes: str = ""
    is_correction: bool = False
    corrects_id: UUID | None = None
    items: list[RecordReceiptItemInput] = field(default_factory=list)


@dataclass(frozen=True)
class RecordGoodsReceiptResult:
    receipt_id: UUID
    receipt_number: str
    purchase_order_id: UUID
    receipt_type: str
    is_fully_inspected: bool


@transaction.atomic
def execute(data: RecordGoodsReceiptInput) -> RecordGoodsReceiptResult:
    """Record physical delivery or service completion against a purchase order."""
    check_permission(data.context, "procurement:receipts:record")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    if data.context.actor_id is None:
        raise ProcurementError("Actor ID is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise ProcurementError("Cannot record receipt for an inactive organization.")

    try:
        order = PurchaseOrder.objects.get(id=data.purchase_order_id)
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found.") from exc

    if order.organization_id != org.id:
        raise OrganizationMismatchError("Purchase order does not belong to this organization.")

    if order.status != PurchaseOrderStatus.ISSUED.value:
        raise ProcurementError(
            f"Cannot record goods receipt against an order in '{order.status}' status. Order must be issued."
        )

    valid_types = {t.value for t in ReceiptType}
    if data.receipt_type not in valid_types:
        raise ProcurementError(f"Invalid receipt type '{data.receipt_type}'. Must be one of {sorted(valid_types)}.")

    if not data.items:
        raise ProcurementError("A goods receipt must contain at least one item.")

    corrects_grn = None
    if data.is_correction and data.corrects_id:
        try:
            corrects_grn = GoodsReceiptNote.objects.get(
                id=data.corrects_id,
                organization_id=org.id,
            )
        except GoodsReceiptNote.DoesNotExist as exc:
            raise GoodsReceiptNotFoundError("Original goods receipt not found.") from exc

        if corrects_grn.purchase_order_id != order.id:
            raise ProcurementError("Correction goods receipt must reference the same purchase order.")

    receipt_number = generate_document_number(org.id, "GRN", GoodsReceiptNote)

    grn = GoodsReceiptNote.objects.create(
        organization_id=org.id,
        receipt_number=receipt_number,
        purchase_order=order,
        receipt_type=data.receipt_type,
        received_date=data.received_date,
        received_by=data.context.actor_id,
        inspection_notes=data.inspection_notes.strip(),
        is_correction=data.is_correction,
        corrects=corrects_grn,
    )

    over_receipt_warnings: list[str] = []

    for item_input in data.items:
        try:
            po_item = PurchaseOrderItem.objects.select_for_update().get(id=item_input.po_item_id)
        except PurchaseOrderItem.DoesNotExist as exc:
            raise ProcurementError("Purchase order item not found.") from exc

        if po_item.purchase_order_id != order.id:
            raise OrganizationMismatchError("Purchase order item does not belong to the specified purchase order.")

        already_received = sum(
            (ri.quantity_received for ri in po_item.receipt_items.all()),
            Decimal("0.00"),
        )
        validate_receipt_quantity(
            item_input.quantity_received,
            po_item.quantity,
            already_received,
        )

        total_after = already_received + item_input.quantity_received
        if total_after > po_item.quantity:
            over_receipt_warnings.append(f"{po_item.description}: received {total_after} vs ordered {po_item.quantity}")

        GoodsReceiptItem.objects.create(
            goods_receipt=grn,
            po_item=po_item,
            quantity_received=item_input.quantity_received,
            quantity_accepted=Decimal("0.00"),
            quantity_rejected=Decimal("0.00"),
            is_inspected=False,
        )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="procurement.receipt.recorded",
        target_type="procurement.GoodsReceiptNote",
        target_id=grn.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "receipt_number": grn.receipt_number,
            "purchase_order_id": str(order.id),
            "item_count": len(data.items),
            "over_receipt_warnings": over_receipt_warnings if over_receipt_warnings else None,
        },
    )

    return RecordGoodsReceiptResult(
        receipt_id=grn.id,
        receipt_number=grn.receipt_number,
        purchase_order_id=grn.purchase_order_id,
        receipt_type=grn.receipt_type,
        is_fully_inspected=grn.is_fully_inspected,
    )
