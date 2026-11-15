from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.fundraising.models import Donor


@dataclass(frozen=True)
class DonorSummaryResult:
    id: UUID
    organization_id: UUID
    name: str
    donor_type: str
    email: str
    status: str
    is_active: bool


def execute(organization_id: UUID) -> list[DonorSummaryResult]:
    """List all donors belonging to the active organization (§6.3)."""
    donors = Donor.objects.filter(organization_id=organization_id).order_by("name")
    return [
        DonorSummaryResult(
            id=d.id,
            organization_id=d.organization_id,
            name=d.name,
            donor_type=d.donor_type,
            email=d.email,
            status=d.status,
            is_active=d.is_active,
        )
        for d in donors
    ]
