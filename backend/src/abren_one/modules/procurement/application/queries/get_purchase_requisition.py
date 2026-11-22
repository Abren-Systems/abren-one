from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    RequisitionNotFoundError,
)
from abren_one.modules.procurement.models import PurchaseRequisition
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RequisitionItemDetailDto:
    id: UUID
    description: str
    quantity: Decimal
    unit: str
    estimated_unit_price: Decimal
    line_total: Decimal
    program_id: UUID | None
    activity_id: UUID | None
    department_id: UUID | None
    allocated_quantity: Decimal
    outstanding_quantity: Decimal


@dataclass(frozen=True)
class RequisitionDetailResult:
    id: UUID
    requisition_number: str
    title: str
    authorization_status: str
    currency: str
    total_estimated_cost: Decimal
    requested_by: UUID
    approved_by: UUID | None
    approved_at: datetime | None
    rejection_reason: str
    notes: str
    created_at: datetime
    updated_at: datetime
    items: list[RequisitionItemDetailDto]


def execute(context: ExecutionContext, requisition_id: UUID) -> RequisitionDetailResult:
    """Retrieve full details of a purchase requisition including items and allocation position."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        req = (
            PurchaseRequisition.objects.filter(
                id=requisition_id,
                organization_id=context.organization_id,
            )
            .prefetch_related("items__allocations")
            .get()
        )
    except PurchaseRequisition.DoesNotExist as exc:
        raise RequisitionNotFoundError("Purchase requisition not found in this organization.") from exc

    items_dto: list[RequisitionItemDetailDto] = []
    for item in req.items.all():
        allocated = sum((a.allocated_quantity for a in item.allocations.all()), Decimal("0.00"))
        qty = Decimal(str(item.quantity))
        outstanding = max(Decimal("0.00"), qty - allocated)
        items_dto.append(
            RequisitionItemDetailDto(
                id=item.id,
                description=item.description,
                quantity=qty,
                unit=item.unit,
                estimated_unit_price=Decimal(str(item.estimated_unit_price)),
                line_total=item.line_total,
                program_id=item.program_id,
                activity_id=item.activity_id,
                department_id=item.department_id,
                allocated_quantity=allocated,
                outstanding_quantity=outstanding,
            )
        )

    return RequisitionDetailResult(
        id=req.id,
        requisition_number=req.requisition_number,
        title=req.title,
        authorization_status=req.authorization_status,
        currency=req.currency,
        total_estimated_cost=req.total_estimated_cost,
        requested_by=req.requested_by,
        approved_by=req.approved_by,
        approved_at=req.approved_at,
        rejection_reason=req.rejection_reason,
        notes=req.notes,
        created_at=req.created_at,
        updated_at=req.updated_at,
        items=items_dto,
    )
