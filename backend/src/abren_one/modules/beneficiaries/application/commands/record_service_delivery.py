from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.beneficiaries.application.bridges.inventory_stock import (
    issue_stock_for_service_delivery,
)
from abren_one.modules.beneficiaries.domain.exceptions import (
    BeneficiaryError,
    BeneficiaryNotFoundError,
    InactiveBeneficiaryError,
)
from abren_one.modules.beneficiaries.domain.value_objects import (
    BeneficiaryStatus,
    DeliveryStatus,
    ServiceType,
)
from abren_one.modules.beneficiaries.models import Beneficiary, ServiceDelivery
from abren_one.modules.programs.public import (
    ActivityNotFoundError,
    ProgramNotFoundError,
    get_activity,
    get_program,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RecordServiceDeliveryInput:
    context: ExecutionContext
    beneficiary_id: UUID
    service_type: str
    delivery_date: date
    quantity: Decimal = Decimal("1.00")
    unit: str = "unit"
    program_id: UUID | None = None
    activity_id: UUID | None = None
    notes: str = ""
    status: str = DeliveryStatus.DELIVERED.value
    # Optional inventory aid distribution bridge (ADR-006)
    warehouse_id: UUID | None = None
    item_id: UUID | None = None
    batch_id: UUID | None = None
    location_id: UUID | None = None


@dataclass(frozen=True)
class RecordServiceDeliveryResult:
    delivery_id: UUID
    inventory_transaction_id: UUID | None = None
    inventory_transaction_number: str = ""


@transaction.atomic
def execute(data: RecordServiceDeliveryInput) -> RecordServiceDeliveryResult:
    """Record an aid or service delivery to a beneficiary (§6.2).

    Cross-module interactions:
    - If program_id is provided, validates existence via Programs public API.
    - If activity_id is provided, validates existence via Programs public API.
    """
    check_permission(data.context, "service_deliveries:record")

    if data.context.organization_id is None:
        raise BeneficiaryError("Organization context is required.")

    try:
        beneficiary = Beneficiary.objects.get(
            id=data.beneficiary_id,
            organization_id=data.context.organization_id,
        )
    except Beneficiary.DoesNotExist as exc:
        raise BeneficiaryNotFoundError(f"Beneficiary {data.beneficiary_id} not found.") from exc

    if beneficiary.status != BeneficiaryStatus.ACTIVE.value:
        raise InactiveBeneficiaryError(f"Cannot deliver services to beneficiary in '{beneficiary.status}' status.")

    if data.quantity < 0:
        raise BeneficiaryError("Service delivery quantity must be non-negative.")

    try:
        ServiceType(data.service_type)
    except ValueError as exc:
        raise BeneficiaryError(f"Invalid service type: '{data.service_type}'.") from exc

    try:
        DeliveryStatus(data.status)
    except ValueError as exc:
        raise BeneficiaryError(f"Invalid delivery status: '{data.status}'.") from exc

    if data.program_id is not None:
        try:
            program = get_program(
                organization_id=data.context.organization_id,
                program_id=data.program_id,
            )
            if not program.is_active:
                raise BeneficiaryError("Cannot deliver services under an inactive program.")
        except ProgramNotFoundError as exc:
            raise BeneficiaryError(f"Program {data.program_id} not found in this organization.") from exc

    if data.activity_id is not None:
        try:
            get_activity(
                organization_id=data.context.organization_id,
                activity_id=data.activity_id,
            )
        except ActivityNotFoundError as exc:
            raise BeneficiaryError(f"Activity {data.activity_id} not found in this organization.") from exc

    delivery = ServiceDelivery.objects.create(
        organization_id=data.context.organization_id,
        beneficiary=beneficiary,
        service_type=data.service_type,
        status=data.status,
        delivery_date=data.delivery_date,
        quantity=data.quantity,
        unit=data.unit,
        notes=data.notes,
        program_id=data.program_id,
        activity_id=data.activity_id,
    )

    # ── Optional Inventory Stock Issue Bridge (ADR-006) ───────────────
    inv_txn_id: UUID | None = None
    inv_txn_number: str = ""
    if data.warehouse_id and data.item_id:
        issue_res = issue_stock_for_service_delivery(
            context=data.context,
            delivery_id=delivery.id,
            warehouse_id=data.warehouse_id,
            item_id=data.item_id,
            quantity=data.quantity,
            delivery_date=data.delivery_date,
            beneficiary_name=beneficiary.display_name,
            service_type=data.service_type,
            batch_id=data.batch_id,
            location_id=data.location_id,
            program_id=data.program_id,
            activity_id=data.activity_id,
            notes=data.notes,
        )
        inv_txn_id = issue_res.transaction_id
        inv_txn_number = issue_res.transaction_number

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="service_delivery.recorded",
        target_type="beneficiaries.ServiceDelivery",
        target_id=delivery.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={
            "service_type": delivery.service_type,
            "quantity": str(delivery.quantity),
            "beneficiary_id": str(beneficiary.id),
            "inventory_transaction_id": str(inv_txn_id) if inv_txn_id else None,
            "inventory_transaction_number": inv_txn_number or None,
        },
    )

    return RecordServiceDeliveryResult(
        delivery_id=delivery.id,
        inventory_transaction_id=inv_txn_id,
        inventory_transaction_number=inv_txn_number,
    )
