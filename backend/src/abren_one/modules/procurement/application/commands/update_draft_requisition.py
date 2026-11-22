from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.public import get_department
from abren_one.modules.procurement.application.commands.create_purchase_requisition import (
    CreateRequisitionItemInput,
)
from abren_one.modules.procurement.domain.exceptions import (
    InvalidRequisitionTransitionError,
    ProcurementError,
    RequisitionNotFoundError,
)
from abren_one.modules.procurement.domain.value_objects import AuthorizationStatus
from abren_one.modules.procurement.models import PurchaseRequisition, RequisitionItem
from abren_one.modules.programs.public import get_activity, get_program
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateDraftRequisitionInput:
    context: ExecutionContext
    requisition_id: UUID
    title: str | None = None
    currency: str | None = None
    notes: str | None = None
    items: list[CreateRequisitionItemInput] | None = None


@dataclass(frozen=True)
class UpdateDraftRequisitionResult:
    requisition_id: UUID
    requisition_number: str
    title: str
    authorization_status: str
    total_estimated_cost: Decimal


@transaction.atomic
def execute(data: UpdateDraftRequisitionInput) -> UpdateDraftRequisitionResult:
    """Update details or line items of a DRAFT purchase requisition."""
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

    if requisition.authorization_status != AuthorizationStatus.DRAFT.value:
        raise InvalidRequisitionTransitionError("Only draft purchase requisitions can be modified.")

    if data.title is not None:
        title = data.title.strip()
        if not title:
            raise ProcurementError("Requisition title cannot be empty.")
        requisition.title = title

    if data.currency is not None:
        requisition.currency = data.currency.strip().upper() or "USD"

    if data.notes is not None:
        requisition.notes = data.notes.strip()

    if data.items is not None:
        requisition.items.all().delete()
        for item_input in data.items:
            desc = item_input.description.strip()
            if not desc:
                raise ProcurementError("Item description cannot be empty.")
            if item_input.quantity <= Decimal("0"):
                raise ProcurementError("Item quantity must be greater than zero.")
            if item_input.estimated_unit_price < Decimal("0"):
                raise ProcurementError("Item estimated unit price cannot be negative.")

            if item_input.program_id is not None:
                prog = get_program(
                    organization_id=requisition.organization_id,
                    program_id=item_input.program_id,
                )
                if prog.organization_id != requisition.organization_id:
                    raise ProcurementError("Referenced program does not belong to this organization.")

            if item_input.activity_id is not None:
                act = get_activity(
                    organization_id=requisition.organization_id,
                    activity_id=item_input.activity_id,
                )
                if act.organization_id != requisition.organization_id:
                    raise ProcurementError("Referenced activity does not belong to this organization.")

            if item_input.department_id is not None:
                dept = get_department(
                    organization_id=requisition.organization_id,
                    department_id=item_input.department_id,
                )
                if dept.organization_id != requisition.organization_id:
                    raise ProcurementError("Referenced department does not belong to this organization.")

            RequisitionItem.objects.create(
                requisition=requisition,
                description=desc,
                quantity=item_input.quantity,
                unit=item_input.unit.strip() or "each",
                estimated_unit_price=item_input.estimated_unit_price,
                program_id=item_input.program_id,
                activity_id=item_input.activity_id,
                department_id=item_input.department_id,
            )

    requisition.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=requisition.organization_id,
        action="procurement.requisition.updated",
        target_type="procurement.PurchaseRequisition",
        target_id=requisition.id,
        correlation_id=data.context.correlation_id,
        metadata={"requisition_number": requisition.requisition_number},
    )

    return UpdateDraftRequisitionResult(
        requisition_id=requisition.id,
        requisition_number=requisition.requisition_number,
        title=requisition.title,
        authorization_status=requisition.authorization_status,
        total_estimated_cost=requisition.total_estimated_cost,
    )
