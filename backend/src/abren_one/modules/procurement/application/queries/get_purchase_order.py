from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    PurchaseOrderNotFoundError,
)
from abren_one.modules.procurement.models import PurchaseOrder
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class PurchaseOrderItemDetailDto:
    id: UUID
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    line_total: Decimal
    quantity_received: Decimal
    quantity_accepted: Decimal
    quantity_outstanding: Decimal


@dataclass(frozen=True)
class PurchaseOrderDetailResult:
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
    issued_by: UUID | None
    expected_delivery_date: date | None
    delivery_address: str
    terms_and_conditions: str
    cancellation_reason: str
    cancelled_by: UUID | None
    cancelled_at: datetime | None
    notes: str
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseOrderItemDetailDto]


def execute(context: ExecutionContext, order_id: UUID) -> PurchaseOrderDetailResult:
    """Retrieve full details of a purchase order including items and delivery positions."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        order = (
            PurchaseOrder.objects.filter(
                id=order_id,
                organization_id=context.organization_id,
            )
            .select_related("vendor", "requisition")
            .prefetch_related("items__receipt_items")
            .get()
        )
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found in this organization.") from exc

    items_dto: list[PurchaseOrderItemDetailDto] = []
    for item in order.items.all():
        received = sum((ri.quantity_received for ri in item.receipt_items.all()), Decimal("0.00"))
        accepted = sum((ri.quantity_accepted for ri in item.receipt_items.all()), Decimal("0.00"))
        qty = Decimal(str(item.quantity))
        outstanding = max(Decimal("0.00"), qty - accepted)
        items_dto.append(
            PurchaseOrderItemDetailDto(
                id=item.id,
                description=item.description,
                quantity=qty,
                unit=item.unit,
                unit_price=Decimal(str(item.unit_price)),
                line_total=item.line_total,
                quantity_received=received,
                quantity_accepted=accepted,
                quantity_outstanding=outstanding,
            )
        )

    return PurchaseOrderDetailResult(
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
        issued_by=order.issued_by,
        expected_delivery_date=order.expected_delivery_date,
        delivery_address=order.delivery_address,
        terms_and_conditions=order.terms_and_conditions,
        cancellation_reason=order.cancellation_reason,
        cancelled_by=order.cancelled_by,
        cancelled_at=order.cancelled_at,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items_dto,
    )
