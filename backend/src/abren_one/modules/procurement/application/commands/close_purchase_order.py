from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    PurchaseOrderNotFoundError,
)
from abren_one.modules.procurement.domain.policies import validate_po_transition
from abren_one.modules.procurement.domain.value_objects import PurchaseOrderStatus
from abren_one.modules.procurement.models import PurchaseOrder
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ClosePurchaseOrderInput:
    context: ExecutionContext
    order_id: UUID


@dataclass(frozen=True)
class ClosePurchaseOrderResult:
    order_id: UUID
    order_number: str
    status: str


@transaction.atomic
def execute(data: ClosePurchaseOrderInput) -> ClosePurchaseOrderResult:
    """Explicitly close an issued purchase order."""
    check_permission(data.context, "procurement:orders:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        order = PurchaseOrder.objects.select_for_update().get(
            id=data.order_id,
            organization_id=data.context.organization_id,
        )
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found in this organization.") from exc

    validate_po_transition(order.status, PurchaseOrderStatus.CLOSED.value)

    order.status = PurchaseOrderStatus.CLOSED.value
    order.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=order.organization_id,
        action="procurement.order.closed",
        target_type="procurement.PurchaseOrder",
        target_id=order.id,
        correlation_id=data.context.correlation_id,
        metadata={"order_number": order.order_number},
    )

    return ClosePurchaseOrderResult(
        order_id=order.id,
        order_number=order.order_number,
        status=order.status,
    )
