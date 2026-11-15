from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.fundraising.domain.exceptions import (
    DonorNotFoundError,
    FundraisingError,
)
from abren_one.modules.fundraising.domain.policies import (
    validate_donation_amount,
    validate_donor_active,
)
from abren_one.modules.fundraising.domain.value_objects import GrantStatus
from abren_one.modules.fundraising.models import Donor, Grant
from abren_one.modules.organizations.public import get_organization
from abren_one.modules.programs.public import ProgramNotFoundError, get_program
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateGrantInput:
    context: ExecutionContext
    donor_id: UUID
    title: str
    reference_code: str
    total_amount: Decimal
    start_date: date
    end_date: date
    currency: str = "USD"
    program_id: UUID | None = None


@dataclass(frozen=True)
class CreateGrantResult:
    grant_id: UUID


@transaction.atomic
def execute(data: CreateGrantInput) -> CreateGrantResult:
    """Create a grant agreement within the active organization (§6.2)."""
    if data.context.organization_id is None:
        raise FundraisingError("Organization context is required.")
    org_id = data.context.organization_id

    org = get_organization(organization_id=org_id)
    if not org.is_active:
        raise FundraisingError("Cannot create a grant for an inactive or suspended organization.")

    validate_donation_amount(data.total_amount)

    if data.end_date < data.start_date:
        raise FundraisingError("Grant end_date cannot precede start_date.")

    donor = Donor.objects.filter(id=data.donor_id, organization_id=org.id).first()
    if not donor:
        raise DonorNotFoundError(f"Donor {data.donor_id} not found in this organization.")

    validate_donor_active(donor.is_active)

    if Grant.objects.filter(organization_id=org.id, reference_code=data.reference_code).exists():
        raise FundraisingError(
            f"A grant with reference code '{data.reference_code}' already exists in this organization."
        )

    if data.program_id is not None:
        try:
            program = get_program(program_id=data.program_id, organization_id=org.id)
            if not program.is_active:
                raise FundraisingError("Cannot link grant to an inactive program.")
        except ProgramNotFoundError as exc:
            raise FundraisingError(f"Program {data.program_id} not found in this organization.") from exc

    grant = Grant.objects.create(
        organization_id=org.id,
        donor=donor,
        title=data.title,
        reference_code=data.reference_code,
        total_amount=data.total_amount,
        currency=data.currency,
        start_date=data.start_date,
        end_date=data.end_date,
        status=GrantStatus.PROPOSED.value,
        program_id=data.program_id,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="fundraising.grant.created",
        target_type="fundraising.Grant",
        target_id=grant.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={
            "reference_code": grant.reference_code,
            "total_amount": str(grant.total_amount),
            "currency": grant.currency,
        },
    )

    return CreateGrantResult(grant_id=grant.id)
