from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.fundraising.domain.exceptions import GrantNotFoundError
from abren_one.modules.fundraising.models import Grant


@dataclass(frozen=True)
class GetGrantResult:
    id: UUID
    organization_id: UUID
    donor_id: UUID
    title: str
    reference_code: str
    total_amount: Decimal
    currency: str
    start_date: date
    end_date: date
    status: str
    is_active: bool
    program_id: UUID | None


def execute(grant_id: UUID, organization_id: UUID) -> GetGrantResult:
    """Retrieve grant details within the active organization (§6.3)."""
    grant = Grant.objects.filter(id=grant_id, organization_id=organization_id).first()
    if not grant:
        raise GrantNotFoundError(f"Grant {grant_id} not found in this organization.")

    return GetGrantResult(
        id=grant.id,
        organization_id=grant.organization_id,
        donor_id=grant.donor_id,
        title=grant.title,
        reference_code=grant.reference_code,
        total_amount=grant.total_amount,
        currency=grant.currency,
        start_date=grant.start_date,
        end_date=grant.end_date,
        status=grant.status,
        is_active=grant.is_active,
        program_id=grant.program_id,
    )
