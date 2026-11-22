from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.public import get_organization
from abren_one.modules.procurement.application.number_generation import (
    generate_document_number,
)
from abren_one.modules.procurement.domain.exceptions import (
    OrganizationMismatchError,
    ProcurementError,
    RequisitionNotFoundError,
    VendorNotFoundError,
)
from abren_one.modules.procurement.domain.policies import (
    validate_allocation_quantity,
    validate_vendor_active,
)
from abren_one.modules.procurement.domain.value_objects import (
    AuthorizationStatus,
    PurchaseOrderStatus,
)
from abren_one.modules.procurement.models import (
    OrderLineAllocation,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseRequisition,
    RequisitionItem,
    Vendor,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateAllocationInput:
    requisition_item_id: UUID
    allocated_quantity: Decimal


@dataclass(frozen=True)
class CreatePurchaseOrderItemInput:
    description: str
    quantity: Decimal
    unit: str = "each"
    unit_price: Decimal = Decimal("0.00")
    allocations: list[CreateAllocationInput] = field(default_factory=list)


@dataclass(frozen=True)
class CreatePurchaseOrderInput:
    context: ExecutionContext
    vendor_id: UUID
    requisition_id: UUID | None = None
    currency: str = "USD"
    expected_delivery_date: date | None = None
    delivery_address: str = ""
    terms_and_conditions: str = ""
    notes: str = ""
    items: list[CreatePurchaseOrderItemInput] = field(default_factory=list)


@dataclass(frozen=True)
class CreatePurchaseOrderResult:
    order_id: UUID
    order_number: str
    vendor_id: UUID
    status: str
    total_amount: Decimal


@transaction.atomic
def execute(data: CreatePurchaseOrderInput) -> CreatePurchaseOrderResult:
    """Create a new purchase order in DRAFT status with items and allocations."""
    check_permission(data.context, "procurement:orders:manage")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise ProcurementError("Cannot create order for an inactive organization.")

    try:
        vendor = Vendor.objects.get(id=data.vendor_id)
    except Vendor.DoesNotExist as exc:
        raise VendorNotFoundError("Vendor not found.") from exc

    if vendor.organization_id != org.id:
        raise OrganizationMismatchError("Vendor does not belong to this organization.")

    validate_vendor_active(vendor.is_active)

    requisition = None
    if data.requisition_id:
        try:
            requisition = PurchaseRequisition.objects.get(id=data.requisition_id)
        except PurchaseRequisition.DoesNotExist as exc:
            raise RequisitionNotFoundError("Purchase requisition not found.") from exc

        if requisition.organization_id != org.id:
            raise OrganizationMismatchError("Purchase requisition does not belong to this organization.")

        if requisition.authorization_status != AuthorizationStatus.APPROVED.value:
            raise ProcurementError("Purchase order can only be created against an approved requisition.")

    order_number = generate_document_number(org.id, "PO", PurchaseOrder)

    order = PurchaseOrder.objects.create(
        organization_id=org.id,
        order_number=order_number,
        vendor=vendor,
        requisition=requisition,
        status=PurchaseOrderStatus.DRAFT.value,
        currency=data.currency.strip().upper() or vendor.default_currency or "USD",
        payment_terms=vendor.default_payment_terms,
        expected_delivery_date=data.expected_delivery_date,
        delivery_address=data.delivery_address.strip(),
        terms_and_conditions=data.terms_and_conditions.strip(),
        notes=data.notes.strip(),
    )

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

            if req_item.requisition.organization_id != org.id:
                raise OrganizationMismatchError("Requisition item does not belong to this organization.")

            if requisition is not None and req_item.requisition_id != requisition.id:
                raise ProcurementError("Allocated requisition item does not belong to the selected requisition.")

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

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="procurement.order.created",
        target_type="procurement.PurchaseOrder",
        target_id=order.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "order_number": order.order_number,
            "vendor_id": str(order.vendor_id),
            "item_count": len(data.items),
        },
    )

    return CreatePurchaseOrderResult(
        order_id=order.id,
        order_number=order.order_number,
        vendor_id=order.vendor_id,
        status=order.status,
        total_amount=order.total_amount,
    )
