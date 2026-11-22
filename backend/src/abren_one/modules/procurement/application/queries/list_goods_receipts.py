from dataclasses import dataclass
from datetime import date
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import ProcurementError
from abren_one.modules.procurement.models import GoodsReceiptNote
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class GoodsReceiptSummaryResult:
    id: UUID
    receipt_number: str
    purchase_order_id: UUID
    order_number: str
    receipt_type: str
    received_date: date
    received_by: UUID
    is_correction: bool
    is_fully_inspected: bool
    has_rejections: bool
    item_count: int


def execute(
    context: ExecutionContext,
    purchase_order_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[GoodsReceiptSummaryResult]:
    """List goods receipts for the active organization with optional PO filter."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    qs = (
        GoodsReceiptNote.objects.filter(organization_id=context.organization_id)
        .select_related("purchase_order")
        .prefetch_related("items")
    )
    if purchase_order_id:
        qs = qs.filter(purchase_order_id=purchase_order_id)

    results: list[GoodsReceiptSummaryResult] = []
    for grn in qs[offset : offset + limit]:
        results.append(
            GoodsReceiptSummaryResult(
                id=grn.id,
                receipt_number=grn.receipt_number,
                purchase_order_id=grn.purchase_order_id,
                order_number=grn.purchase_order.order_number if grn.purchase_order else "",
                receipt_type=grn.receipt_type,
                received_date=grn.received_date,
                received_by=grn.received_by,
                is_correction=grn.is_correction,
                is_fully_inspected=grn.is_fully_inspected,
                has_rejections=grn.has_rejections,
                item_count=grn.items.count(),
            )
        )
    return results
