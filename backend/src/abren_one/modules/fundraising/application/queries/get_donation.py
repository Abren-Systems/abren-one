from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.fundraising.domain.exceptions import DonationNotFoundError
from abren_one.modules.fundraising.models import Donation


@dataclass(frozen=True)
class GetDonationResult:
    id: UUID
    organization_id: UUID
    donor_id: UUID
    donor_name: str
    grant_id: UUID | None
    amount: Decimal
    currency: str
    received_at: datetime
    payment_method: str
    status: str
    program_id: UUID | None


def execute(donation_id: UUID, organization_id: UUID) -> GetDonationResult:
    """Retrieve donation details within the active organization (§6.3)."""
    donation = Donation.objects.filter(id=donation_id, organization_id=organization_id).select_related("donor").first()
    if not donation:
        raise DonationNotFoundError(f"Donation {donation_id} not found in this organization.")

    return GetDonationResult(
        id=donation.id,
        organization_id=donation.organization_id,
        donor_id=donation.donor_id,
        donor_name=donation.donor.name,
        grant_id=donation.grant_id,
        amount=donation.amount,
        currency=donation.currency,
        received_at=donation.received_at,
        payment_method=donation.payment_method,
        status=donation.status,
        program_id=donation.program_id,
    )
