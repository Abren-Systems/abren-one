from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.beneficiaries.domain.exceptions import (
    BeneficiaryError,
    BeneficiaryNotFoundError,
    InvalidBeneficiaryTransitionError,
)
from abren_one.modules.beneficiaries.domain.policies import (
    can_transition_beneficiary_status,
)
from abren_one.modules.beneficiaries.domain.value_objects import BeneficiaryStatus
from abren_one.modules.beneficiaries.models import Beneficiary
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateBeneficiaryInput:
    context: ExecutionContext
    beneficiary_id: UUID
    first_name: str | None = None
    last_name: str | None = None
    household_name: str | None = None
    status: str | None = None
    vulnerability_level: str | None = None
    contact_phone: str | None = None
    contact_address: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class UpdateBeneficiaryResult:
    beneficiary_id: UUID
    status: str


@transaction.atomic
def execute(data: UpdateBeneficiaryInput) -> UpdateBeneficiaryResult:
    """Update beneficiary details or transition status (§6.2)."""
    check_permission(data.context, "beneficiaries:manage")

    if data.context.organization_id is None:
        raise BeneficiaryError("Organization context is required.")

    try:
        beneficiary = Beneficiary.objects.select_for_update().get(
            id=data.beneficiary_id,
            organization_id=data.context.organization_id,
        )
    except Beneficiary.DoesNotExist as exc:
        raise BeneficiaryNotFoundError(f"Beneficiary {data.beneficiary_id} not found.") from exc

    if data.status is not None and data.status != beneficiary.status:
        try:
            target_status = BeneficiaryStatus(data.status)
        except ValueError as exc:
            raise BeneficiaryError(f"Invalid beneficiary status: '{data.status}'.") from exc

        current_status = BeneficiaryStatus(beneficiary.status)
        if not can_transition_beneficiary_status(current_status, target_status):
            raise InvalidBeneficiaryTransitionError(
                f"Cannot transition beneficiary from '{beneficiary.status}' to '{data.status}'."
            )
        beneficiary.status = target_status.value

    if data.first_name is not None:
        beneficiary.first_name = data.first_name

    if data.last_name is not None:
        beneficiary.last_name = data.last_name

    if data.household_name is not None:
        beneficiary.household_name = data.household_name

    if data.vulnerability_level is not None:
        beneficiary.vulnerability_level = data.vulnerability_level

    if data.contact_phone is not None:
        beneficiary.contact_phone = data.contact_phone

    if data.contact_address is not None:
        beneficiary.contact_address = data.contact_address

    if data.notes is not None:
        beneficiary.notes = data.notes

    beneficiary.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="beneficiary.updated",
        target_type="beneficiaries.Beneficiary",
        target_id=beneficiary.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"display_name": beneficiary.display_name, "status": beneficiary.status},
    )

    return UpdateBeneficiaryResult(beneficiary_id=beneficiary.id, status=beneficiary.status)
