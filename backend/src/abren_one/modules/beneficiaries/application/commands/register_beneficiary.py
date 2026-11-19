from dataclasses import dataclass
from datetime import date
from uuid import UUID

from django.db import transaction

from abren_one.modules.beneficiaries.domain.exceptions import BeneficiaryError
from abren_one.modules.beneficiaries.domain.value_objects import (
    BeneficiaryStatus,
    BeneficiaryType,
    Gender,
    VulnerabilityLevel,
)
from abren_one.modules.beneficiaries.models import Beneficiary
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RegisterBeneficiaryInput:
    context: ExecutionContext
    beneficiary_type: str = BeneficiaryType.INDIVIDUAL.value
    identification_number: str = ""
    first_name: str = ""
    last_name: str = ""
    household_name: str = ""
    date_of_birth: date | None = None
    gender: str = Gender.UNSPECIFIED.value
    vulnerability_level: str = VulnerabilityLevel.MEDIUM.value
    contact_phone: str = ""
    contact_address: str = ""
    notes: str = ""


@dataclass(frozen=True)
class RegisterBeneficiaryResult:
    beneficiary_id: UUID


@transaction.atomic
def execute(data: RegisterBeneficiaryInput) -> RegisterBeneficiaryResult:
    """Register a new beneficiary in the active organization (§6.2)."""
    if data.context.organization_id is None:
        raise BeneficiaryError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise BeneficiaryError("Cannot register beneficiary for an inactive or suspended organization.")

    if (
        data.identification_number
        and Beneficiary.objects.filter(
            organization_id=org.id,
            identification_number=data.identification_number,
        ).exists()
    ):
        raise BeneficiaryError(
            f"A beneficiary with identification number "
            f"'{data.identification_number}' already exists in this organization."
        )

    beneficiary = Beneficiary.objects.create(
        organization_id=org.id,
        beneficiary_type=data.beneficiary_type,
        identification_number=data.identification_number,
        first_name=data.first_name,
        last_name=data.last_name,
        household_name=data.household_name,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        status=BeneficiaryStatus.ACTIVE.value,
        vulnerability_level=data.vulnerability_level,
        contact_phone=data.contact_phone,
        contact_address=data.contact_address,
        notes=data.notes,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="beneficiary.registered",
        target_type="beneficiaries.Beneficiary",
        target_id=beneficiary.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={
            "beneficiary_type": beneficiary.beneficiary_type,
            "display_name": beneficiary.display_name,
        },
    )

    return RegisterBeneficiaryResult(beneficiary_id=beneficiary.id)
