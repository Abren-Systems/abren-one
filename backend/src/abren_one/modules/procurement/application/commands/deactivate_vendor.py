from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.procurement.domain.exceptions import (
    ProcurementError,
    VendorNotFoundError,
)
from abren_one.modules.procurement.models import Vendor
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class DeactivateVendorInput:
    context: ExecutionContext
    vendor_id: UUID
    reason: str


@dataclass(frozen=True)
class DeactivateVendorResult:
    vendor_id: UUID
    is_active: bool
    deactivation_reason: str


@transaction.atomic
def execute(data: DeactivateVendorInput) -> DeactivateVendorResult:
    """Deactivate a vendor with an explicit reason."""
    check_permission(data.context, "procurement:vendors:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    reason = data.reason.strip()
    if not reason:
        raise ProcurementError("Deactivation reason cannot be empty.")

    try:
        vendor = Vendor.objects.select_for_update().get(
            id=data.vendor_id,
            organization_id=data.context.organization_id,
        )
    except Vendor.DoesNotExist as exc:
        raise VendorNotFoundError("Vendor not found in this organization.") from exc

    vendor.is_active = False
    vendor.deactivation_reason = reason
    vendor.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=data.context.organization_id,
        action="procurement.vendor.deactivated",
        target_type="procurement.Vendor",
        target_id=vendor.id,
        correlation_id=data.context.correlation_id,
        metadata={"reason": reason},
    )

    return DeactivateVendorResult(
        vendor_id=vendor.id,
        is_active=vendor.is_active,
        deactivation_reason=vendor.deactivation_reason,
    )
