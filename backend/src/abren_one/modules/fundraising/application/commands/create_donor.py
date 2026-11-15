from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.fundraising.domain.exceptions import (
    FundraisingError,
)
from abren_one.modules.fundraising.domain.value_objects import (
    DonorStatus,
    DonorType,
)
from abren_one.modules.fundraising.models import Donor
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateDonorInput:
    context: ExecutionContext
    name: str
    donor_type: str = DonorType.INDIVIDUAL.value
    email: str = ""
    phone: str = ""


@dataclass(frozen=True)
class CreateDonorResult:
    donor_id: UUID


@transaction.atomic
def execute(data: CreateDonorInput) -> CreateDonorResult:
    """Create a new donor in the active organization (§6.2)."""
    assert data.context.organization_id is not None, "Organization context is required."
    org_id = data.context.organization_id

    org = get_organization(organization_id=org_id)
    if not org.is_active:
        raise FundraisingError("Cannot create a donor for an inactive or suspended organization.")

    if Donor.objects.filter(organization_id=org.id, name=data.name).exists():
        raise FundraisingError(f"A donor named '{data.name}' already exists in this organization.")

    donor = Donor.objects.create(
        organization_id=org.id,
        name=data.name,
        donor_type=data.donor_type,
        email=data.email,
        phone=data.phone,
        status=DonorStatus.ACTIVE.value,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="fundraising.donor.created",
        target_type="fundraising.Donor",
        target_id=donor.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"name": donor.name, "donor_type": donor.donor_type},
    )

    return CreateDonorResult(donor_id=donor.id)
