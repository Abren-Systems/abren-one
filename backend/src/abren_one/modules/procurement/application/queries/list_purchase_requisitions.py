from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import ProcurementError
from abren_one.modules.procurement.models import PurchaseRequisition
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RequisitionSummaryResult:
    id: UUID
    requisition_number: str
    title: str
    authorization_status: str
    currency: str
    total_estimated_cost: Decimal
    requested_by: UUID
    approved_by: UUID | None
    approved_at: datetime | None
    created_at: datetime
    item_count: int


def execute(
    context: ExecutionContext,
    authorization_status: str | None = None,
    requested_by: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[RequisitionSummaryResult]:
    """List purchase requisitions for the active organization with optional filters."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    qs = PurchaseRequisition.objects.filter(
        organization_id=context.organization_id,
    ).prefetch_related("items")
    if authorization_status:
        qs = qs.filter(authorization_status=authorization_status)
    if requested_by:
        qs = qs.filter(requested_by=requested_by)

    results: list[RequisitionSummaryResult] = []
    for req in qs[offset : offset + limit]:
        results.append(
            RequisitionSummaryResult(
                id=req.id,
                requisition_number=req.requisition_number,
                title=req.title,
                authorization_status=req.authorization_status,
                currency=req.currency,
                total_estimated_cost=req.total_estimated_cost,
                requested_by=req.requested_by,
                approved_by=req.approved_by,
                approved_at=req.approved_at,
                created_at=req.created_at,
                item_count=req.items.count(),
            )
        )
    return results
