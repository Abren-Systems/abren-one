from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.public import get_organization
from abren_one.modules.procurement.domain.exceptions import ProcurementError
from abren_one.modules.procurement.domain.value_objects import VendorType
from abren_one.modules.procurement.models import Vendor
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateVendorInput:
    context: ExecutionContext
    name: str
    vendor_type: str = VendorType.GOODS.value
    tax_id: str = ""
    country: str = ""
    contact_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    default_payment_terms: str = ""
    default_currency: str = "USD"
    notes: str = ""


@dataclass(frozen=True)
class CreateVendorResult:
    vendor_id: UUID
    name: str
    vendor_type: str
    is_active: bool
    verification_status: str


@transaction.atomic
def execute(data: CreateVendorInput) -> CreateVendorResult:
    """Create a new supplier master vendor record."""
    check_permission(data.context, "procurement:vendors:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise ProcurementError("Cannot create vendor for an inactive organization.")

    name = data.name.strip()
    if not name:
        raise ProcurementError("Vendor name cannot be empty.")

    valid_types = {t.value for t in VendorType}
    if data.vendor_type not in valid_types:
        raise ProcurementError(f"Invalid vendor type '{data.vendor_type}'. Must be one of {sorted(valid_types)}.")

    if Vendor.objects.filter(organization_id=org.id, name=name).exists():
        raise ProcurementError(f"Vendor with name '{name}' already exists in this organization.")

    tax_id = data.tax_id.strip()
    if tax_id and Vendor.objects.filter(organization_id=org.id, tax_id=tax_id).exists():
        raise ProcurementError(f"Vendor with tax ID '{tax_id}' already exists in this organization.")

    vendor = Vendor.objects.create(
        organization_id=org.id,
        name=name,
        vendor_type=data.vendor_type,
        tax_id=tax_id,
        country=data.country.strip()[:3],
        contact_name=data.contact_name.strip(),
        email=data.email.strip(),
        phone=data.phone.strip(),
        address=data.address.strip(),
        default_payment_terms=data.default_payment_terms.strip(),
        default_currency=data.default_currency.strip().upper() or "USD",
        notes=data.notes.strip(),
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="procurement.vendor.created",
        target_type="procurement.Vendor",
        target_id=vendor.id,
        correlation_id=data.context.correlation_id,
        metadata={"name": vendor.name, "vendor_type": vendor.vendor_type},
    )

    return CreateVendorResult(
        vendor_id=vendor.id,
        name=vendor.name,
        vendor_type=vendor.vendor_type,
        is_active=vendor.is_active,
        verification_status=vendor.verification_status,
    )
