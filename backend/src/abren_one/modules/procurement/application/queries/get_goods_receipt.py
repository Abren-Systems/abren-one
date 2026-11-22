from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    GoodsReceiptNotFoundError,
    ProcurementError,
)
from abren_one.modules.procurement.models import GoodsReceiptNote
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class GoodsReceiptItemDetailDto:
    id: UUID
    po_item_id: UUID
    description: str
    quantity_received: Decimal
    quantity_accepted: Decimal
    quantity_rejected: Decimal
    is_inspected: bool
    rejection_reason: str


@dataclass(frozen=True)
class GoodsReceiptDetailResult:
    id: UUID
    receipt_number: str
    purchase_order_id: UUID
    order_number: str
    receipt_type: str
    received_date: date
    received_by: UUID
    inspection_notes: str
    is_correction: bool
    corrects_id: UUID | None
    is_fully_inspected: bool
    has_rejections: bool
    created_at: datetime
    updated_at: datetime
    items: list[GoodsReceiptItemDetailDto]


def execute(context: ExecutionContext, receipt_id: UUID) -> GoodsReceiptDetailResult:
    """Retrieve full details of a goods receipt note including line items."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        grn = (
            GoodsReceiptNote.objects.filter(
                id=receipt_id,
                organization_id=context.organization_id,
            )
            .select_related("purchase_order")
            .prefetch_related("items__po_item")
            .get()
        )
    except GoodsReceiptNote.DoesNotExist as exc:
        raise GoodsReceiptNotFoundError("Goods receipt note not found in this organization.") from exc

    items_dto: list[GoodsReceiptItemDetailDto] = [
        GoodsReceiptItemDetailDto(
            id=item.id,
            po_item_id=item.po_item_id,
            description=item.po_item.description if item.po_item else "",
            quantity_received=Decimal(str(item.quantity_received)),
            quantity_accepted=Decimal(str(item.quantity_accepted)),
            quantity_rejected=Decimal(str(item.quantity_rejected)),
            is_inspected=item.is_inspected,
            rejection_reason=item.rejection_reason,
        )
        for item in grn.items.all()
    ]

    return GoodsReceiptDetailResult(
        id=grn.id,
        receipt_number=grn.receipt_number,
        purchase_order_id=grn.purchase_order_id,
        order_number=grn.purchase_order.order_number if grn.purchase_order else "",
        receipt_type=grn.receipt_type,
        received_date=grn.received_date,
        received_by=grn.received_by,
        inspection_notes=grn.inspection_notes,
        is_correction=grn.is_correction,
        corrects_id=grn.corrects_id,
        is_fully_inspected=grn.is_fully_inspected,
        has_rejections=grn.has_rejections,
        created_at=grn.created_at,
        updated_at=grn.updated_at,
        items=items_dto,
    )
