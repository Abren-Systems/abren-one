from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.procurement.application.commands.create_purchase_order import (
    CreatePurchaseOrderItemInput,
)
from abren_one.modules.procurement.domain.exceptions import (
    InvalidPurchaseOrderTransitionError,
    OrganizationMismatchError,
    ProcurementError,
    PurchaseOrderNotFoundError,
    VendorNotFoundError,
)
from abren_one.modules.procurement.domain.policies import (
    validate_allocation_quantity,
    validate_vendor_active,
)
from abren_one.modules.procurement.domain.value_objects import PurchaseOrderStatus
from abren_one.modules.procurement.models import (
    OrderLineAllocation,
    PurchaseOrder,
    PurchaseOrderItem,
    RequisitionItem,
    Vendor,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateDraftPurchaseOrderInput:
    context: ExecutionContext
    order_id: UUID
    vendor_id: UUID | None = None
    currency: str | None = None
    expected_delivery_date: date | None = None
    delivery_address: str | None = None
    terms_and_conditions: str | None = None
    notes: str | None = None
    items: list[CreatePurchaseOrderItemInput] | None = None


@dataclass(frozen=True)
class UpdateDraftPurchaseOrderResult:
    order_id: UUID
    order_number: str
    status: str
    total_amount: Decimal


@transaction.atomic
def execute(data: UpdateDraftPurchaseOrderInput) -> UpdateDraftPurchaseOrderResult:
    """Update details or line items of a DRAFT purchase order."""
    check_permission(data.context, "procurement:orders:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        order = PurchaseOrder.objects.select_for_update().get(
            id=data.order_id,
            organization_id=data.context.organization_id,
        )
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found in this organization.") from exc

    if order.status != PurchaseOrderStatus.DRAFT.value:
        raise InvalidPurchaseOrderTransitionError("Only draft purchase orders can be modified.")

    if data.vendor_id is not None:
        try:
            vendor = Vendor.objects.get(id=data.vendor_id)
        except Vendor.DoesNotExist as exc:
            raise VendorNotFoundError("Vendor not found.") from exc

        if vendor.organization_id != order.organization_id:
            raise OrganizationMismatchError("Vendor does not belong to this organization.")

        validate_vendor_active(vendor.is_active)
        order.vendor = vendor
        order.payment_terms = vendor.default_payment_terms

    if data.currency is not None:
        order.currency = data.currency.strip().upper() or "USD"

    if data.expected_delivery_date is not None:
        order.expected_delivery_date = data.expected_delivery_date

    if data.delivery_address is not None:
        order.delivery_address = data.delivery_address.strip()

    if data.terms_and_conditions is not None:
        order.terms_and_conditions = data.terms_and_conditions.strip()

    if data.notes is not None:
        order.notes = data.notes.strip()

    if data.items is not None:
        # Delete existing items (which cascades to allocations)
        order.items.all().delete()

        for item_input in data.items:
            desc = item_input.description.strip()
            if not desc:
                raise ProcurementError("Item description cannot be empty.")
            if item_input.quantity <= Decimal("0"):
                raise ProcurementError("Item quantity must be greater than zero.")
            if item_input.unit_price < Decimal("0"):
                raise ProcurementError("Item unit price cannot be negative.")

            po_item = PurchaseOrderItem.objects.create(
                purchase_order=order,
                description=desc,
                quantity=item_input.quantity,
                unit=item_input.unit.strip() or "each",
                unit_price=item_input.unit_price,
            )

            for alloc_input in item_input.allocations:
                try:
                    req_item = RequisitionItem.objects.select_for_update().get(
                        id=alloc_input.requisition_item_id,
                    )
                except RequisitionItem.DoesNotExist as exc:
                    raise ProcurementError("Requisition item not found.") from exc

                if req_item.requisition.organization_id != order.organization_id:
                    raise OrganizationMismatchError("Requisition item does not belong to this organization.")

                already_allocated = sum(
                    (a.allocated_quantity for a in req_item.allocations.all()),
                    Decimal("0.00"),
                )
                validate_allocation_quantity(
                    alloc_input.allocated_quantity,
                    req_item.quantity,
                    already_allocated,
                )

                OrderLineAllocation.objects.create(
                    requisition_item=req_item,
                    po_item=po_item,
                    allocated_quantity=alloc_input.allocated_quantity,
                )

    order.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=order.organization_id,
        action="procurement.order.updated",
        target_type="procurement.PurchaseOrder",
        target_id=order.id,
        correlation_id=data.context.correlation_id,
        metadata={"order_number": order.order_number},
    )

    return UpdateDraftPurchaseOrderResult(
        order_id=order.id,
        order_number=order.order_number,
        status=order.status,
        total_amount=order.total_amount,
    )
