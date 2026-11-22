from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    PurchaseOrderNotFoundError,
)
from abren_one.modules.procurement.models import PurchaseOrder
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class OrderItemDeliveryDto:
    po_item_id: UUID
    description: str
    quantity_ordered: Decimal
    unit: str
    unit_price: Decimal
    quantity_received: Decimal
    quantity_accepted: Decimal
    quantity_rejected: Decimal
    quantity_outstanding: Decimal


@dataclass(frozen=True)
class OrderDeliveryPositionResult:
    order_id: UUID
    order_number: str
    status: str
    delivery_position: str
    items: list[OrderItemDeliveryDto]


def execute(context: ExecutionContext, order_id: UUID) -> OrderDeliveryPositionResult:
    """Compute the derived delivery position of a purchase order across its goods receipts."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        order = (
            PurchaseOrder.objects.filter(
                id=order_id,
                organization_id=context.organization_id,
            )
            .prefetch_related("items__receipt_items")
            .get()
        )
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found in this organization.") from exc

    items_dto: list[OrderItemDeliveryDto] = []
    all_fully_accepted = True
    any_received = False
    any_over_delivered = False

    for item in order.items.all():
        qty_ord = Decimal(str(item.quantity))
        qty_rec = sum((ri.quantity_received for ri in item.receipt_items.all()), Decimal("0.00"))
        qty_acc = sum((ri.quantity_accepted for ri in item.receipt_items.all()), Decimal("0.00"))
        qty_rej = sum((ri.quantity_rejected for ri in item.receipt_items.all()), Decimal("0.00"))
        qty_out = max(Decimal("0.00"), qty_ord - qty_acc)

        if qty_rec > Decimal("0.00"):
            any_received = True

        if qty_acc < qty_ord:
            all_fully_accepted = False

        if qty_acc > qty_ord:
            any_over_delivered = True

        items_dto.append(
            OrderItemDeliveryDto(
                po_item_id=item.id,
                description=item.description,
                quantity_ordered=qty_ord,
                unit=item.unit,
                unit_price=Decimal(str(item.unit_price)),
                quantity_received=qty_rec,
                quantity_accepted=qty_acc,
                quantity_rejected=qty_rej,
                quantity_outstanding=qty_out,
            )
        )

    if not any_received:
        pos = "NOT_DELIVERED"
    elif all_fully_accepted:
        pos = "OVER_DELIVERED" if any_over_delivered else "FULLY_DELIVERED"
    else:
        pos = "PARTIALLY_DELIVERED"

    return OrderDeliveryPositionResult(
        order_id=order.id,
        order_number=order.order_number,
        status=order.status,
        delivery_position=pos,
        items=items_dto,
    )
