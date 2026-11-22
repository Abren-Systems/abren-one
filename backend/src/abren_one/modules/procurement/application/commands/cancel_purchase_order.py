from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    PurchaseOrderNotFoundError,
)
from abren_one.modules.procurement.domain.policies import (
    validate_po_can_cancel,
    validate_po_transition,
)
from abren_one.modules.procurement.domain.value_objects import PurchaseOrderStatus
from abren_one.modules.procurement.models import GoodsReceiptItem, PurchaseOrder
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CancelPurchaseOrderInput:
    context: ExecutionContext
    order_id: UUID
    cancellation_reason: str


@dataclass(frozen=True)
class CancelPurchaseOrderResult:
    order_id: UUID
    order_number: str
    status: str
    cancellation_reason: str
    cancelled_by: UUID
    cancelled_at: datetime


@transaction.atomic
def execute(data: CancelPurchaseOrderInput) -> CancelPurchaseOrderResult:
    """Cancel a purchase order if no goods have been accepted."""
    check_permission(data.context, "procurement:orders:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    if data.context.actor_id is None:
        raise ProcurementError("Actor ID is required.")

    reason = data.cancellation_reason.strip()
    if not reason:
        raise ProcurementError("Cancellation reason cannot be empty.")

    try:
        order = PurchaseOrder.objects.select_for_update().get(
            id=data.order_id,
            organization_id=data.context.organization_id,
        )
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found in this organization.") from exc

    validate_po_transition(order.status, PurchaseOrderStatus.CANCELLED.value)

    has_accepted_receipts = GoodsReceiptItem.objects.filter(
        po_item__purchase_order=order,
        quantity_accepted__gt=0,
    ).exists()
    validate_po_can_cancel(has_accepted_receipts)

    now = timezone.now()
    order.status = PurchaseOrderStatus.CANCELLED.value
    order.cancellation_reason = reason
    order.cancelled_by = data.context.actor_id
    order.cancelled_at = now
    order.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=order.organization_id,
        action="procurement.order.cancelled",
        target_type="procurement.PurchaseOrder",
        target_id=order.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "order_number": order.order_number,
            "cancellation_reason": reason,
            "cancelled_by": str(data.context.actor_id),
        },
    )

    return CancelPurchaseOrderResult(
        order_id=order.id,
        order_number=order.order_number,
        status=order.status,
        cancellation_reason=reason,
        cancelled_by=data.context.actor_id,
        cancelled_at=now,
    )
