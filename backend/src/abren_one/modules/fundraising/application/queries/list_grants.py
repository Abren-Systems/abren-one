from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from abren_one.modules.fundraising.models import Grant


@dataclass(frozen=True)
class GrantSummaryResult:
    id: UUID
    organization_id: UUID
    donor_id: UUID
    title: str
    reference_code: str
    total_amount: Decimal
    currency: str
    status: str
    is_active: bool


def execute(organization_id: UUID, donor_id: UUID | None = None) -> list[GrantSummaryResult]:
    """List grants for the active organization (§6.3)."""
    qs = Grant.objects.filter(organization_id=organization_id)
    if donor_id is not None:
        qs = qs.filter(donor_id=donor_id)

    grants = qs.order_by("-start_date")
    return [
        GrantSummaryResult(
            id=g.id,
            organization_id=g.organization_id,
            donor_id=g.donor_id,
            title=g.title,
            reference_code=g.reference_code,
            total_amount=g.total_amount,
            currency=g.currency,
            status=g.status,
            is_active=g.is_active,
        )
        for g in grants
    ]
