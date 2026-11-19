from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.beneficiaries.domain.exceptions import (
    ServiceDeliveryNotFoundError,
)
from abren_one.modules.beneficiaries.models import ServiceDelivery


@dataclass(frozen=True)
class GetServiceDeliveryResult:
    id: UUID
    organization_id: UUID
    beneficiary_id: UUID
    beneficiary_name: str
    service_type: str
    status: str
    delivery_date: date
    quantity: Decimal
    unit: str
    notes: str
    program_id: UUID | None
    activity_id: UUID | None


def execute(*, organization_id: UUID, delivery_id: UUID) -> GetServiceDeliveryResult:
    """Retrieve full service delivery record within the active organization."""
    try:
        d = ServiceDelivery.objects.select_related("beneficiary").get(
            id=delivery_id,
            organization_id=organization_id,
        )
    except ServiceDelivery.DoesNotExist as exc:
        raise ServiceDeliveryNotFoundError(f"Service delivery {delivery_id} not found.") from exc

    return GetServiceDeliveryResult(
        id=d.id,
        organization_id=d.organization_id,
        beneficiary_id=d.beneficiary_id,
        beneficiary_name=d.beneficiary.display_name,
        service_type=d.service_type,
        status=d.status,
        delivery_date=d.delivery_date,
        quantity=d.quantity,
        unit=d.unit,
        notes=d.notes,
        program_id=d.program_id,
        activity_id=d.activity_id,
    )
