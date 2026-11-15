from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.fundraising.domain.exceptions import DonorNotFoundError
from abren_one.modules.fundraising.models import Donor


@dataclass(frozen=True)
class GetDonorResult:
    id: UUID
    organization_id: UUID
    name: str
    donor_type: str
    email: str
    phone: str
    status: str
    is_active: bool


def execute(donor_id: UUID, organization_id: UUID) -> GetDonorResult:
    """Retrieve donor details within the active organization (§6.3)."""
    donor = Donor.objects.filter(id=donor_id, organization_id=organization_id).first()
    if not donor:
        raise DonorNotFoundError(f"Donor {donor_id} not found in this organization.")

    return GetDonorResult(
        id=donor.id,
        organization_id=donor.organization_id,
        name=donor.name,
        donor_type=donor.donor_type,
        email=donor.email,
        phone=donor.phone,
        status=donor.status,
        is_active=donor.is_active,
    )
