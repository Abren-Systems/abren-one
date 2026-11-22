from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import ProcurementError
from abren_one.modules.procurement.models import PurchaseOrder
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class PurchaseOrderSummaryResult:
    id: UUID
    order_number: str
    vendor_id: UUID
    vendor_name: str
    requisition_id: UUID | None
    requisition_number: str
    status: str
    currency: str
    total_amount: Decimal
    payment_terms: str
    issued_at: datetime | None
    created_at: datetime
    item_count: int


def execute(
    context: ExecutionContext,
    status: str | None = None,
    vendor_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[PurchaseOrderSummaryResult]:
    """List purchase orders for the active organization with optional filters."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    qs = (
        PurchaseOrder.objects.filter(organization_id=context.organization_id)
        .select_related("vendor", "requisition")
        .prefetch_related("items")
    )
    if status:
        qs = qs.filter(status=status)
    if vendor_id:
        qs = qs.filter(vendor_id=vendor_id)

    results: list[PurchaseOrderSummaryResult] = []
    for order in qs[offset : offset + limit]:
        results.append(
            PurchaseOrderSummaryResult(
                id=order.id,
                order_number=order.order_number,
                vendor_id=order.vendor_id,
                vendor_name=order.vendor.name if order.vendor else "",
                requisition_id=order.requisition_id,
                requisition_number=order.requisition.requisition_number if order.requisition else "",
                status=order.status,
                currency=order.currency,
                total_amount=order.total_amount,
                payment_terms=order.payment_terms,
                issued_at=order.issued_at,
                created_at=order.created_at,
                item_count=order.items.count(),
            )
        )
    return results
