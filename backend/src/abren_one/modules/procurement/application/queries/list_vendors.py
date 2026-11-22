from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import ProcurementError
from abren_one.modules.procurement.models import Vendor
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class VendorSummaryResult:
    id: UUID
    name: str
    vendor_type: str
    tax_id: str
    country: str
    contact_name: str
    email: str
    is_active: bool
    verification_status: str
    default_currency: str


def execute(
    context: ExecutionContext,
    vendor_type: str | None = None,
    is_active: bool | None = None,
    verification_status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[VendorSummaryResult]:
    """List vendors for the active organization with optional filters."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    qs = Vendor.objects.filter(organization_id=context.organization_id)
    if vendor_type:
        qs = qs.filter(vendor_type=vendor_type)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if verification_status:
        qs = qs.filter(verification_status=verification_status)

    return [
        VendorSummaryResult(
            id=v.id,
            name=v.name,
            vendor_type=v.vendor_type,
            tax_id=v.tax_id,
            country=v.country,
            contact_name=v.contact_name,
            email=v.email,
            is_active=v.is_active,
            verification_status=v.verification_status,
            default_currency=v.default_currency,
        )
        for v in qs[offset : offset + limit]
    ]
