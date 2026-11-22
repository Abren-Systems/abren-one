from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.public import get_department, get_organization
from abren_one.modules.procurement.application.number_generation import (
    generate_document_number,
)
from abren_one.modules.procurement.domain.exceptions import ProcurementError
from abren_one.modules.procurement.domain.value_objects import AuthorizationStatus
from abren_one.modules.procurement.models import PurchaseRequisition, RequisitionItem
from abren_one.modules.programs.public import get_activity, get_program
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateRequisitionItemInput:
    description: str
    quantity: Decimal
    unit: str = "each"
    estimated_unit_price: Decimal = Decimal("0.00")
    program_id: UUID | None = None
    activity_id: UUID | None = None
    department_id: UUID | None = None


@dataclass(frozen=True)
class CreatePurchaseRequisitionInput:
    context: ExecutionContext
    title: str
    items: list[CreateRequisitionItemInput] = field(default_factory=list)
    currency: str = "USD"
    notes: str = ""


@dataclass(frozen=True)
class CreatePurchaseRequisitionResult:
    requisition_id: UUID
    requisition_number: str
    title: str
    authorization_status: str
    total_estimated_cost: Decimal


@transaction.atomic
def execute(data: CreatePurchaseRequisitionInput) -> CreatePurchaseRequisitionResult:
    """Create a new purchase requisition in DRAFT status."""
    check_permission(data.context, "procurement:requisitions:create")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    if data.context.actor_id is None:
        raise ProcurementError("Actor ID is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise ProcurementError("Cannot create requisition for an inactive organization.")

    title = data.title.strip()
    if not title:
        raise ProcurementError("Requisition title cannot be empty.")

    req_number = generate_document_number(org.id, "PR", PurchaseRequisition)

    requisition = PurchaseRequisition.objects.create(
        organization_id=org.id,
        requisition_number=req_number,
        title=title,
        authorization_status=AuthorizationStatus.DRAFT.value,
        requested_by=data.context.actor_id,
        currency=data.currency.strip().upper() or "USD",
        notes=data.notes.strip(),
    )

    for item_input in data.items:
        desc = item_input.description.strip()
        if not desc:
            raise ProcurementError("Item description cannot be empty.")
        if item_input.quantity <= Decimal("0"):
            raise ProcurementError("Item quantity must be greater than zero.")
        if item_input.estimated_unit_price < Decimal("0"):
            raise ProcurementError("Item estimated unit price cannot be negative.")

        # Soft reference cross-module integrity validation
        if item_input.program_id is not None:
            prog = get_program(organization_id=org.id, program_id=item_input.program_id)
            if prog.organization_id != org.id:
                raise ProcurementError("Referenced program does not belong to this organization.")

        if item_input.activity_id is not None:
            act = get_activity(organization_id=org.id, activity_id=item_input.activity_id)
            if act.organization_id != org.id:
                raise ProcurementError("Referenced activity does not belong to this organization.")

        if item_input.department_id is not None:
            dept = get_department(organization_id=org.id, department_id=item_input.department_id)
            if dept.organization_id != org.id:
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

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="procurement.requisition.created",
        target_type="procurement.PurchaseRequisition",
        target_id=requisition.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "requisition_number": requisition.requisition_number,
            "title": requisition.title,
            "item_count": len(data.items),
        },
    )

    return CreatePurchaseRequisitionResult(
        requisition_id=requisition.id,
        requisition_number=requisition.requisition_number,
        title=requisition.title,
        authorization_status=requisition.authorization_status,
        total_estimated_cost=requisition.total_estimated_cost,
    )
