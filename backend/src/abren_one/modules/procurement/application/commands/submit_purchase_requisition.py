from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    RequisitionNotFoundError,
)
from abren_one.modules.procurement.domain.policies import (
    validate_authorization_transition,
    validate_requisition_has_items,
)
from abren_one.modules.procurement.domain.value_objects import AuthorizationStatus
from abren_one.modules.procurement.models import PurchaseRequisition
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class SubmitPurchaseRequisitionInput:
    context: ExecutionContext
    requisition_id: UUID


@dataclass(frozen=True)
class SubmitPurchaseRequisitionResult:
    requisition_id: UUID
    requisition_number: str
    authorization_status: str


@transaction.atomic
def execute(data: SubmitPurchaseRequisitionInput) -> SubmitPurchaseRequisitionResult:
    """Submit a draft purchase requisition for authorization."""
    check_permission(data.context, "procurement:requisitions:create")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        requisition = PurchaseRequisition.objects.select_for_update().get(
            id=data.requisition_id,
            organization_id=data.context.organization_id,
        )
    except PurchaseRequisition.DoesNotExist as exc:
        raise RequisitionNotFoundError("Purchase requisition not found in this organization.") from exc

    validate_authorization_transition(
        requisition.authorization_status,
        AuthorizationStatus.SUBMITTED.value,
    )
    validate_requisition_has_items(requisition.items.count())

    requisition.authorization_status = AuthorizationStatus.SUBMITTED.value
    requisition.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=requisition.organization_id,
        action="procurement.requisition.submitted",
        target_type="procurement.PurchaseRequisition",
        target_id=requisition.id,
        correlation_id=data.context.correlation_id,
        metadata={"requisition_number": requisition.requisition_number},
    )

    return SubmitPurchaseRequisitionResult(
        requisition_id=requisition.id,
        requisition_number=requisition.requisition_number,
        authorization_status=requisition.authorization_status,
    )
