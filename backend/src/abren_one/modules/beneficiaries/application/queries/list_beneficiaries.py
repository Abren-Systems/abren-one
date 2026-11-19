from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.beneficiaries.models import Beneficiary


@dataclass(frozen=True)
class BeneficiarySummaryResult:
    id: UUID
    organization_id: UUID
    beneficiary_type: str
    identification_number: str
    display_name: str
    status: str
    vulnerability_level: str
    is_active: bool


def execute(
    *,
    organization_id: UUID,
    status: str | None = None,
    beneficiary_type: str | None = None,
) -> list[BeneficiarySummaryResult]:
    """List beneficiaries for an organization, with optional status and type filters."""
    qs = Beneficiary.objects.filter(organization_id=organization_id)
    if status is not None:
        qs = qs.filter(status=status)
    if beneficiary_type is not None:
        qs = qs.filter(beneficiary_type=beneficiary_type)

    return [
        BeneficiarySummaryResult(
            id=b.id,
            organization_id=b.organization_id,
            beneficiary_type=b.beneficiary_type,
            identification_number=b.identification_number,
            display_name=b.display_name,
            status=b.status,
            vulnerability_level=b.vulnerability_level,
            is_active=b.is_active,
        )
        for b in qs
    ]
