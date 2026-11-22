from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    RequisitionNotFoundError,
)
from abren_one.modules.procurement.domain.policies import (
    validate_authorization_transition,
)
from abren_one.modules.procurement.domain.value_objects import AuthorizationStatus
from abren_one.modules.procurement.models import PurchaseRequisition
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ReturnRequisitionToDraftInput:
    context: ExecutionContext
    requisition_id: UUID


@dataclass(frozen=True)
class ReturnRequisitionToDraftResult:
    requisition_id: UUID
    requisition_number: str
    authorization_status: str


@transaction.atomic
def execute(data: ReturnRequisitionToDraftInput) -> ReturnRequisitionToDraftResult:
    """Return a submitted or rejected requisition to DRAFT status for revision."""
    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        requisition = PurchaseRequisition.objects.select_for_update().get(
            id=data.requisition_id,
            organization_id=data.context.organization_id,
        )
    except PurchaseRequisition.DoesNotExist as exc:
        raise RequisitionNotFoundError("Purchase requisition not found in this organization.") from exc

    # Check appropriate permission based on current status
    if requisition.authorization_status == AuthorizationStatus.REJECTED.value:
        check_permission(data.context, "procurement:requisitions:create")
    else:
        check_permission(data.context, "procurement:requisitions:approve")

    validate_authorization_transition(
        requisition.authorization_status,
        AuthorizationStatus.DRAFT.value,
    )

    requisition.authorization_status = AuthorizationStatus.DRAFT.value
    requisition.rejection_reason = ""
    requisition.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=requisition.organization_id,
        action="procurement.requisition.returned",
        target_type="procurement.PurchaseRequisition",
        target_id=requisition.id,
        correlation_id=data.context.correlation_id,
        metadata={"requisition_number": requisition.requisition_number},
    )

    return ReturnRequisitionToDraftResult(
        requisition_id=requisition.id,
        requisition_number=requisition.requisition_number,
        authorization_status=requisition.authorization_status,
    )
