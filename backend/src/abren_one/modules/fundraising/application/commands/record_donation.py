from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from abren_one.modules.fundraising.domain.exceptions import (
    DonorNotFoundError,
    FundraisingError,
    GrantMismatchError,
    GrantNotFoundError,
)
from abren_one.modules.fundraising.domain.policies import (
    validate_donation_amount,
    validate_donor_active,
)
from abren_one.modules.fundraising.domain.value_objects import (
    DonationStatus,
    PaymentMethod,
)
from abren_one.modules.fundraising.models import Donation, Donor, Grant
from abren_one.modules.organizations.public import get_organization
from abren_one.modules.programs.public import ProgramNotFoundError, get_program
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RecordDonationInput:
    context: ExecutionContext
    donor_id: UUID
    amount: Decimal
    currency: str = "USD"
    payment_method: str = PaymentMethod.BANK_TRANSFER.value
    reference: str = ""
    received_at: datetime | None = None
    grant_id: UUID | None = None
    program_id: UUID | None = None


@dataclass(frozen=True)
class RecordDonationResult:
    donation_id: UUID


@transaction.atomic
def execute(data: RecordDonationInput) -> RecordDonationResult:
    """Record a monetary donation received from a supporter (§6.2, §Appendix B)."""
    check_permission(data.context, "donations:record")

    if data.context.organization_id is None:
        raise FundraisingError("Organization context is required.")
    org_id = data.context.organization_id

    org = get_organization(organization_id=org_id)
    if not org.is_active:
        raise FundraisingError("Cannot record a donation for an inactive or suspended organization.")

    validate_donation_amount(data.amount)

    donor = Donor.objects.filter(id=data.donor_id, organization_id=org.id).first()
    if not donor:
        raise DonorNotFoundError(f"Donor {data.donor_id} not found in this organization.")

    validate_donor_active(donor.is_active)

    grant: Grant | None = None
    if data.grant_id is not None:
        grant = Grant.objects.filter(id=data.grant_id, organization_id=org.id).first()
        if not grant:
            raise GrantNotFoundError(f"Grant {data.grant_id} not found in this organization.")
        if grant.donor_id != donor.id:
            raise GrantMismatchError(
                f"Grant {data.grant_id} belongs to a different donor than the donation donor {donor.id}."
            )
        if not grant.is_active:
            raise FundraisingError("Cannot record donation against an inactive or closed grant.")

    if data.program_id is not None:
        try:
            program = get_program(program_id=data.program_id, organization_id=org.id)
            if not program.is_active:
                raise FundraisingError("Cannot link donation to an inactive program.")
        except ProgramNotFoundError as exc:
            raise FundraisingError(f"Program {data.program_id} not found in this organization.") from exc

    received_at = data.received_at or timezone.now()

    donation = Donation.objects.create(
        organization_id=org.id,
        donor=donor,
        grant=grant,
        amount=data.amount,
        currency=data.currency,
        received_at=received_at,
        payment_method=data.payment_method,
        reference=data.reference,
        status=DonationStatus.RECEIVED.value,
        program_id=data.program_id,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="fundraising.donation.recorded",
        target_type="fundraising.Donation",
        target_id=donation.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={
            "donor_id": str(donor.id),
            "amount": str(donation.amount),
            "currency": donation.currency,
            "payment_method": donation.payment_method,
            "grant_id": str(grant.id) if grant else None,
            "program_id": str(data.program_id) if data.program_id else None,
        },
    )

    return RecordDonationResult(donation_id=donation.id)
