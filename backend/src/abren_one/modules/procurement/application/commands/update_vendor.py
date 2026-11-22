from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    VendorNotFoundError,
)
from abren_one.modules.procurement.domain.policies import validate_vendor_active
from abren_one.modules.procurement.domain.value_objects import (
    VendorType,
    VendorVerificationStatus,
)
from abren_one.modules.procurement.models import Vendor
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateVendorInput:
    context: ExecutionContext
    vendor_id: UUID
    name: str | None = None
    vendor_type: str | None = None
    tax_id: str | None = None
    country: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    default_payment_terms: str | None = None
    default_currency: str | None = None
    verification_status: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class UpdateVendorResult:
    vendor_id: UUID
    name: str
    vendor_type: str
    is_active: bool
    verification_status: str


@transaction.atomic
def execute(data: UpdateVendorInput) -> UpdateVendorResult:
    """Update details of an active vendor."""
    check_permission(data.context, "procurement:vendors:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        vendor = Vendor.objects.select_for_update().get(
            id=data.vendor_id,
            organization_id=data.context.organization_id,
        )
    except Vendor.DoesNotExist as exc:
        raise VendorNotFoundError("Vendor not found in this organization.") from exc

    validate_vendor_active(vendor.is_active)

    before_state = {
        "name": vendor.name,
        "vendor_type": vendor.vendor_type,
        "verification_status": vendor.verification_status,
    }

    if data.name is not None:
        name = data.name.strip()
        if not name:
            raise ProcurementError("Vendor name cannot be empty.")
        if (
            Vendor.objects.filter(
                organization_id=data.context.organization_id,
                name=name,
            )
            .exclude(id=vendor.id)
            .exists()
        ):
            raise ProcurementError(f"Vendor with name '{name}' already exists.")
        vendor.name = name

    if data.vendor_type is not None:
        valid_types = {t.value for t in VendorType}
        if data.vendor_type not in valid_types:
            raise ProcurementError(f"Invalid vendor type '{data.vendor_type}'. Must be one of {sorted(valid_types)}.")
        vendor.vendor_type = data.vendor_type

    if data.tax_id is not None:
        tax_id = data.tax_id.strip()
        if (
            tax_id
            and Vendor.objects.filter(
                organization_id=data.context.organization_id,
                tax_id=tax_id,
            )
            .exclude(id=vendor.id)
            .exists()
        ):
            raise ProcurementError(f"Vendor with tax ID '{tax_id}' already exists.")
        vendor.tax_id = tax_id

    if data.country is not None:
        vendor.country = data.country.strip()[:3]
    if data.contact_name is not None:
        vendor.contact_name = data.contact_name.strip()
    if data.email is not None:
        vendor.email = data.email.strip()
    if data.phone is not None:
        vendor.phone = data.phone.strip()
    if data.address is not None:
        vendor.address = data.address.strip()
    if data.default_payment_terms is not None:
        vendor.default_payment_terms = data.default_payment_terms.strip()
    if data.default_currency is not None:
        vendor.default_currency = data.default_currency.strip().upper()
    if data.verification_status is not None:
        valid_statuses = {s.value for s in VendorVerificationStatus}
        if data.verification_status not in valid_statuses:
            raise ProcurementError(
                f"Invalid verification status '{data.verification_status}'. Must be one of {sorted(valid_statuses)}."
            )
        vendor.verification_status = data.verification_status
    if data.notes is not None:
        vendor.notes = data.notes.strip()

    vendor.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=data.context.organization_id,
        action="procurement.vendor.updated",
        target_type="procurement.Vendor",
        target_id=vendor.id,
        correlation_id=data.context.correlation_id,
        metadata={"before": before_state, "after": {"name": vendor.name, "vendor_type": vendor.vendor_type}},
    )

    return UpdateVendorResult(
        vendor_id=vendor.id,
        name=vendor.name,
        vendor_type=vendor.vendor_type,
        is_active=vendor.is_active,
        verification_status=vendor.verification_status,
    )
