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
    validate_po_transition,
    validate_vendor_active,
)
from abren_one.modules.procurement.domain.value_objects import PurchaseOrderStatus
from abren_one.modules.procurement.models import PurchaseOrder
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class IssuePurchaseOrderInput:
    context: ExecutionContext
    order_id: UUID


@dataclass(frozen=True)
class IssuePurchaseOrderResult:
    order_id: UUID
    order_number: str
    status: str
    issued_at: datetime
    payment_terms: str


@transaction.atomic
def execute(data: IssuePurchaseOrderInput) -> IssuePurchaseOrderResult:
    """Issue a purchase order to vendor, locking commercial terms."""
    check_permission(data.context, "procurement:orders:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    if data.context.actor_id is None:
        raise ProcurementError("Actor ID is required.")

    try:
        order = PurchaseOrder.objects.select_for_update().get(
            id=data.order_id,
            organization_id=data.context.organization_id,
        )
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found in this organization.") from exc

    validate_po_transition(order.status, PurchaseOrderStatus.ISSUED.value)
    validate_vendor_active(order.vendor.is_active)

    if not order.items.exists():
        raise ProcurementError("Cannot issue a purchase order with no items.")

    now = timezone.now()
    order.status = PurchaseOrderStatus.ISSUED.value
    order.issued_at = now
    order.issued_by = data.context.actor_id
    order.payment_terms = order.vendor.default_payment_terms
    order.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=order.organization_id,
        action="procurement.order.issued",
        target_type="procurement.PurchaseOrder",
        target_id=order.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "order_number": order.order_number,
            "issued_by": str(data.context.actor_id),
            "payment_terms": order.payment_terms,
        },
    )

    return IssuePurchaseOrderResult(
        order_id=order.id,
        order_number=order.order_number,
        status=order.status,
        issued_at=now,
        payment_terms=order.payment_terms,
    )
