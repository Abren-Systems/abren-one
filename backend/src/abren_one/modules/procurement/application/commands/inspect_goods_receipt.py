from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.procurement.domain.exceptions import (
    GoodsReceiptNotFoundError,
    OrganizationMismatchError,
    ProcurementError,
)
from abren_one.modules.procurement.domain.policies import (
    validate_inspection_quantities,
)
from abren_one.modules.procurement.models import (
    GoodsReceiptItem,
    GoodsReceiptNote,
)
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class InspectReceiptItemInput:
    grn_item_id: UUID
    quantity_accepted: Decimal
    quantity_rejected: Decimal
    rejection_reason: str = ""


@dataclass(frozen=True)
class InspectGoodsReceiptInput:
    context: ExecutionContext
    receipt_id: UUID
    inspections: list[InspectReceiptItemInput]


@dataclass(frozen=True)
class InspectGoodsReceiptResult:
    receipt_id: UUID
    receipt_number: str
    is_fully_inspected: bool
    has_rejections: bool


@transaction.atomic
def execute(data: InspectGoodsReceiptInput) -> InspectGoodsReceiptResult:
    """Inspect goods receipt line items with explicit quantity reconciliation."""
    check_permission(data.context, "procurement:receipts:inspect")

    if data.context.organization_id is None:
        raise ProcurementError("Organization context is required.")

    try:
        grn = GoodsReceiptNote.objects.select_for_update().get(
            id=data.receipt_id,
            organization_id=data.context.organization_id,
        )
    except GoodsReceiptNote.DoesNotExist as exc:
        raise GoodsReceiptNotFoundError("Goods receipt note not found in this organization.") from exc

    if not data.inspections:
        raise ProcurementError("At least one inspection item must be provided.")

    for insp in data.inspections:
        try:
            grn_item = GoodsReceiptItem.objects.select_for_update().get(id=insp.grn_item_id)
        except GoodsReceiptItem.DoesNotExist as exc:
            raise ProcurementError("Goods receipt item not found.") from exc

        if grn_item.goods_receipt_id != grn.id:
            raise OrganizationMismatchError("Goods receipt item does not belong to the specified goods receipt.")

        validate_inspection_quantities(
            received=grn_item.quantity_received,
            accepted=insp.quantity_accepted,
            rejected=insp.quantity_rejected,
        )

        grn_item.quantity_accepted = insp.quantity_accepted
        grn_item.quantity_rejected = insp.quantity_rejected
        grn_item.is_inspected = True
        grn_item.rejection_reason = insp.rejection_reason.strip()
        grn_item.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=grn.organization_id,
        action="procurement.receipt.inspected",
        target_type="procurement.GoodsReceiptNote",
        target_id=grn.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "receipt_number": grn.receipt_number,
            "inspected_items_count": len(data.inspections),
            "is_fully_inspected": grn.is_fully_inspected,
            "has_rejections": grn.has_rejections,
        },
    )

    return InspectGoodsReceiptResult(
        receipt_id=grn.id,
        receipt_number=grn.receipt_number,
        is_fully_inspected=grn.is_fully_inspected,
        has_rejections=grn.has_rejections,
    )
