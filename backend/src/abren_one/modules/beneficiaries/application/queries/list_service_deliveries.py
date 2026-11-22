from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.beneficiaries.models import ServiceDelivery


@dataclass(frozen=True)
class ServiceDeliverySummaryResult:
    id: UUID
    organization_id: UUID
    beneficiary_id: UUID
    beneficiary_name: str
    service_type: str
    status: str
    delivery_date: date
    quantity: Decimal
    unit: str
    program_id: UUID | None
    activity_id: UUID | None


def execute(
    *,
    organization_id: UUID,
    beneficiary_id: UUID | None = None,
    program_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[ServiceDeliverySummaryResult]:
    """List service deliveries for an organization, optionally filtered."""
    qs = ServiceDelivery.objects.filter(organization_id=organization_id).select_related("beneficiary")
    if beneficiary_id is not None:
        qs = qs.filter(beneficiary_id=beneficiary_id)
    if program_id is not None:
        qs = qs.filter(program_id=program_id)

    return [
        ServiceDeliverySummaryResult(
            id=d.id,
            organization_id=d.organization_id,
            beneficiary_id=d.beneficiary_id,
            beneficiary_name=d.beneficiary.display_name,
            service_type=d.service_type,
            status=d.status,
            delivery_date=d.delivery_date,
            quantity=d.quantity,
            unit=d.unit,
            program_id=d.program_id,
            activity_id=d.activity_id,
        )
        for d in qs[offset : offset + limit]
    ]
