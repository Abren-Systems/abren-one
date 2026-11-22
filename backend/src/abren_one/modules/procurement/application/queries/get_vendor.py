from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    VendorNotFoundError,
)
from abren_one.modules.procurement.models import Vendor
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class VendorDetailResult:
    id: UUID
    name: str
    vendor_type: str
    tax_id: str
    country: str
    contact_name: str
    email: str
    phone: str
    address: str
    default_payment_terms: str
    default_currency: str
    verification_status: str
    is_active: bool
    deactivation_reason: str
    notes: str
    created_at: datetime
    updated_at: datetime


def execute(context: ExecutionContext, vendor_id: UUID) -> VendorDetailResult:
    """Retrieve full details of a vendor within the active organization."""
    if context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        v = Vendor.objects.get(id=vendor_id, organization_id=context.organization_id)
    except Vendor.DoesNotExist as exc:
        raise VendorNotFoundError("Vendor not found in this organization.") from exc

    return VendorDetailResult(
        id=v.id,
        name=v.name,
        vendor_type=v.vendor_type,
        tax_id=v.tax_id,
        country=v.country,
        contact_name=v.contact_name,
        email=v.email,
        phone=v.phone,
        address=v.address,
        default_payment_terms=v.default_payment_terms,
        default_currency=v.default_currency,
        verification_status=v.verification_status,
        is_active=v.is_active,
        deactivation_reason=v.deactivation_reason,
        notes=v.notes,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )
