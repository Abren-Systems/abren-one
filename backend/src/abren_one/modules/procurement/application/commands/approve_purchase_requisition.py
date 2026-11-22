from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    RequisitionNotFoundError,
)
from abren_one.modules.procurement.domain.policies import (
    validate_authorization_transition,
    validate_no_self_approval,
)
from abren_one.modules.procurement.domain.value_objects import AuthorizationStatus
from abren_one.modules.procurement.models import PurchaseRequisition
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ApprovePurchaseRequisitionInput:
    context: ExecutionContext
    requisition_id: UUID


@dataclass(frozen=True)
class ApprovePurchaseRequisitionResult:
    requisition_id: UUID
    requisition_number: str
    authorization_status: str
    approved_by: UUID
    approved_at: datetime


@transaction.atomic
def execute(data: ApprovePurchaseRequisitionInput) -> ApprovePurchaseRequisitionResult:
    """Approve a submitted purchase requisition, enforcing segregation of duties."""
    check_permission(data.context, "procurement:requisitions:approve")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    if data.context.actor_id is None:
        raise ProcurementError("Actor ID is required.")

    try:
        requisition = PurchaseRequisition.objects.select_for_update().get(
            id=data.requisition_id,
            organization_id=data.context.organization_id,
        )
    except PurchaseRequisition.DoesNotExist as exc:
        raise RequisitionNotFoundError("Purchase requisition not found in this organization.") from exc

    validate_authorization_transition(
        requisition.authorization_status,
        AuthorizationStatus.APPROVED.value,
    )
    validate_no_self_approval(requisition.requested_by, data.context.actor_id)

    now = timezone.now()
    requisition.authorization_status = AuthorizationStatus.APPROVED.value
    requisition.approved_by = data.context.actor_id
    requisition.approved_at = now
    requisition.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=requisition.organization_id,
        action="procurement.requisition.approved",
        target_type="procurement.PurchaseRequisition",
        target_id=requisition.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "requisition_number": requisition.requisition_number,
            "approved_by": str(data.context.actor_id),
        },
    )

    return ApprovePurchaseRequisitionResult(
        requisition_id=requisition.id,
        requisition_number=requisition.requisition_number,
        authorization_status=requisition.authorization_status,
        approved_by=data.context.actor_id,
        approved_at=now,
    )
