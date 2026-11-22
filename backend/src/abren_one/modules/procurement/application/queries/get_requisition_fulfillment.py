from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    RequisitionNotFoundError,
)
from abren_one.modules.procurement.models import PurchaseRequisition
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RequisitionItemFulfillmentDto:
    item_id: UUID
    description: str
    quantity_requested: Decimal
    unit: str
    quantity_ordered: Decimal
    quantity_accepted: Decimal
    quantity_outstanding_order: Decimal
    quantity_outstanding_delivery: Decimal


@dataclass(frozen=True)
class RequisitionFulfillmentResult:
    requisition_id: UUID
    requisition_number: str
    authorization_status: str
    fulfillment_position: str
    items: list[RequisitionItemFulfillmentDto]


def execute(context: ExecutionContext, requisition_id: UUID) -> RequisitionFulfillmentResult:
    """Compute the derived fulfillment position of a requisition across allocations and receipts."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        req = (
            PurchaseRequisition.objects.filter(
                id=requisition_id,
                organization_id=context.organization_id,
            )
            .prefetch_related("items__allocations__po_item__receipt_items")
            .get()
        )
    except PurchaseRequisition.DoesNotExist as exc:
        raise RequisitionNotFoundError("Purchase requisition not found in this organization.") from exc

    items_dto: list[RequisitionItemFulfillmentDto] = []
    total_requested = Decimal("0.00")
    total_ordered = Decimal("0.00")
    total_accepted = Decimal("0.00")

    for item in req.items.all():
        qty_req = Decimal(str(item.quantity))
        qty_ord = sum((a.allocated_quantity for a in item.allocations.all()), Decimal("0.00"))

        qty_acc = Decimal("0.00")
        for alloc in item.allocations.all():
            qty_acc += sum(
                (ri.quantity_accepted for ri in alloc.po_item.receipt_items.all()),
                Decimal("0.00"),
            )

        out_ord = max(Decimal("0.00"), qty_req - qty_ord)
        out_deliv = max(Decimal("0.00"), qty_ord - qty_acc)

        total_requested += qty_req
        total_ordered += qty_ord
        total_accepted += qty_acc

        items_dto.append(
            RequisitionItemFulfillmentDto(
                item_id=item.id,
                description=item.description,
                quantity_requested=qty_req,
                unit=item.unit,
                quantity_ordered=qty_ord,
                quantity_accepted=qty_acc,
                quantity_outstanding_order=out_ord,
                quantity_outstanding_delivery=out_deliv,
            )
        )

    # Derive overall requisition fulfillment position
    if total_ordered == Decimal("0.00"):
        position = "NOT_ORDERED"
    elif total_ordered >= total_requested:
        if total_accepted >= total_requested:
            position = "FULLY_FULFILLED"
        elif total_accepted > Decimal("0.00"):
            position = "PARTIALLY_FULFILLED"
        else:
            position = "FULLY_ORDERED"
    else:
        position = "PARTIALLY_FULFILLED" if total_accepted > Decimal("0.00") else "PARTIALLY_ORDERED"

    return RequisitionFulfillmentResult(
        requisition_id=req.id,
        requisition_number=req.requisition_number,
        authorization_status=req.authorization_status,
        fulfillment_position=position,
        items=items_dto,
    )
