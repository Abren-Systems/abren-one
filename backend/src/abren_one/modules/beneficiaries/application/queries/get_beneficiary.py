from dataclasses import dataclass
from datetime import date
from uuid import UUID

from abren_one.modules.beneficiaries.domain.exceptions import BeneficiaryNotFoundError
from abren_one.modules.beneficiaries.models import Beneficiary


@dataclass(frozen=True)
class GetBeneficiaryResult:
    id: UUID
    organization_id: UUID
    beneficiary_type: str
    identification_number: str
    first_name: str
    last_name: str
    household_name: str
    display_name: str
    date_of_birth: date | None
    gender: str
    status: str
    vulnerability_level: str
    contact_phone: str
    contact_address: str
    notes: str
    is_active: bool


def execute(*, organization_id: UUID, beneficiary_id: UUID) -> GetBeneficiaryResult:
    """Retrieve full beneficiary details within the active organization."""
    try:
        b = Beneficiary.objects.get(id=beneficiary_id, organization_id=organization_id)
    except Beneficiary.DoesNotExist as exc:
        raise BeneficiaryNotFoundError(f"Beneficiary {beneficiary_id} not found.") from exc

    return GetBeneficiaryResult(
        id=b.id,
        organization_id=b.organization_id,
        beneficiary_type=b.beneficiary_type,
        identification_number=b.identification_number,
        first_name=b.first_name,
        last_name=b.last_name,
        household_name=b.household_name,
        display_name=b.display_name,
        date_of_birth=b.date_of_birth,
        gender=b.gender,
        status=b.status,
        vulnerability_level=b.vulnerability_level,
        contact_phone=b.contact_phone,
        contact_address=b.contact_address,
        notes=b.notes,
        is_active=b.is_active,
    )
