from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.fundraising.models import Donation


@dataclass(frozen=True)
class DonationSummaryResult:
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


def execute(organization_id: UUID, donor_id: UUID | None = None) -> list[DonationSummaryResult]:
    """List donations for the active organization (§6.3)."""
    qs = Donation.objects.filter(organization_id=organization_id).select_related("donor")
    if donor_id is not None:
        qs = qs.filter(donor_id=donor_id)

    donations = qs.order_by("-received_at")
    return [
        DonationSummaryResult(
            id=d.id,
            organization_id=d.organization_id,
            donor_id=d.donor_id,
            donor_name=d.donor.name,
            grant_id=d.grant_id,
            amount=d.amount,
            currency=d.currency,
            received_at=d.received_at,
            payment_method=d.payment_method,
            status=d.status,
            program_id=d.program_id,
        )
        for d in donations
    ]
