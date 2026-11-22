"""Public interface for the Procurement module.

Exposes controlled DTOs and query functions for cross-module integration
(e.g., Finance commitment tracking, budget validation, and 3-way matching).
Other modules must import ONLY from this file.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    GoodsReceiptNotFoundError,
    ProcurementError,
    PurchaseOrderNotFoundError,
    RequisitionNotFoundError,
    VendorNotFoundError,
)
from abren_one.modules.procurement.domain.value_objects import (
    AuthorizationStatus,
    PurchaseOrderStatus,
    ReceiptType,
    VendorType,
    VendorVerificationStatus,
)
from abren_one.modules.procurement.models import (
    GoodsReceiptItem,
    PurchaseOrder,
)


@dataclass(frozen=True)
class ProcurementCommitmentItem:
    po_item_id: UUID
    description: str
    quantity_ordered: Decimal
    unit_price: Decimal
    quantity_accepted: Decimal
    quantity_outstanding: Decimal
    line_total: Decimal
    outstanding_value: Decimal
    program_id: UUID | None
    activity_id: UUID | None
    department_id: UUID | None


@dataclass(frozen=True)
class ProcurementCommitmentSummary:
    po_id: UUID
    order_number: str
    vendor_name: str
    vendor_id: UUID
    currency: str
    status: str
    issued_at: datetime | None
    total_committed: Decimal
    total_delivered: Decimal
    total_outstanding: Decimal
    items: list[ProcurementCommitmentItem]


@dataclass(frozen=True)
class AcceptedReceiptItem:
    grn_id: UUID
    receipt_number: str
    po_item_id: UUID
    description: str
    quantity_accepted: Decimal
    unit_price: Decimal
    accepted_value: Decimal
    received_date: date
    program_id: UUID | None


def _build_commitment_summary(order: PurchaseOrder) -> ProcurementCommitmentSummary:
    commitment_items: list[ProcurementCommitmentItem] = []
    total_committed = Decimal("0.00")
    total_delivered = Decimal("0.00")

    for po_item in order.items.all():
        qty_ord = Decimal(str(po_item.quantity))
        unit_p = Decimal(str(po_item.unit_price))
        line_tot = po_item.line_total
        qty_acc = sum(
            (ri.quantity_accepted for ri in po_item.receipt_items.all()),
            Decimal("0.00"),
        )
        qty_out = max(Decimal("0.00"), qty_ord - qty_acc)
        out_val = qty_out * unit_p

        # Derive program/activity/department attribution from requisition item allocation
        alloc = po_item.allocations.select_related("requisition_item").first()
        prog_id = alloc.requisition_item.program_id if alloc and alloc.requisition_item else None
        act_id = alloc.requisition_item.activity_id if alloc and alloc.requisition_item else None
        dept_id = alloc.requisition_item.department_id if alloc and alloc.requisition_item else None

        total_committed += line_tot
        total_delivered += qty_acc * unit_p

        commitment_items.append(
            ProcurementCommitmentItem(
                po_item_id=po_item.id,
                description=po_item.description,
                quantity_ordered=qty_ord,
                unit_price=unit_p,
                quantity_accepted=qty_acc,
                quantity_outstanding=qty_out,
                line_total=line_tot,
                outstanding_value=out_val,
                program_id=prog_id,
                activity_id=act_id,
                department_id=dept_id,
            )
        )

    total_outstanding = max(Decimal("0.00"), total_committed - total_delivered)

    return ProcurementCommitmentSummary(
        po_id=order.id,
        order_number=order.order_number,
        vendor_name=order.vendor.name if order.vendor else "",
        vendor_id=order.vendor_id,
        currency=order.currency,
        status=order.status,
        issued_at=order.issued_at,
        total_committed=total_committed,
        total_delivered=total_delivered,
        total_outstanding=total_outstanding,
        items=commitment_items,
    )


def get_outstanding_commitments(
    organization_id: UUID,
    *,
    program_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[ProcurementCommitmentSummary]:
    """Return issued purchase orders with outstanding delivery/settlement obligations."""
    qs = (
        PurchaseOrder.objects.filter(
            organization_id=organization_id,
            status=PurchaseOrderStatus.ISSUED.value,
        )
        .select_related("vendor")
        .prefetch_related(
            "items__receipt_items",
            "items__allocations__requisition_item",
        )
    )

    if program_id is not None:
        qs = qs.filter(items__allocations__requisition_item__program_id=program_id).distinct()

    summaries: list[ProcurementCommitmentSummary] = []
    for order in qs[offset : offset + limit]:
        summary = _build_commitment_summary(order)
        if summary.total_outstanding > Decimal("0.00"):
            summaries.append(summary)
    return summaries


def get_commitment_detail(
    organization_id: UUID,
    po_id: UUID,
) -> ProcurementCommitmentSummary:
    """Retrieve detailed commitment breakdown for a specific purchase order."""
    try:
        order = (
            PurchaseOrder.objects.filter(
                id=po_id,
                organization_id=organization_id,
            )
            .select_related("vendor")
            .prefetch_related(
                "items__receipt_items",
                "items__allocations__requisition_item",
            )
            .get()
        )
    except PurchaseOrder.DoesNotExist as exc:
        raise PurchaseOrderNotFoundError("Purchase order not found in this organization.") from exc

    return _build_commitment_summary(order)


def get_accepted_receipts_for_order(
    organization_id: UUID,
    po_id: UUID,
) -> list[AcceptedReceiptItem]:
    """Return all accepted receipt line items for a specific purchase order."""
    grn_items = (
        GoodsReceiptItem.objects.filter(
            goods_receipt__organization_id=organization_id,
            po_item__purchase_order_id=po_id,
            quantity_accepted__gt=0,
            is_inspected=True,
        )
        .select_related("goods_receipt", "po_item")
        .prefetch_related("po_item__allocations__requisition_item")
    )

    results: list[AcceptedReceiptItem] = []
    for ri in grn_items:
        alloc = ri.po_item.allocations.first()
        prog_id = alloc.requisition_item.program_id if alloc and alloc.requisition_item else None
        qty_acc = Decimal(str(ri.quantity_accepted))
        unit_p = Decimal(str(ri.po_item.unit_price))
        results.append(
            AcceptedReceiptItem(
                grn_id=ri.goods_receipt_id,
                receipt_number=ri.goods_receipt.receipt_number,
                po_item_id=ri.po_item_id,
                description=ri.po_item.description,
                quantity_accepted=qty_acc,
                unit_price=unit_p,
                accepted_value=qty_acc * unit_p,
                received_date=ri.goods_receipt.received_date,
                program_id=prog_id,
            )
        )
    return results


def get_unmatched_accepted_receipts(
    organization_id: UUID,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[AcceptedReceiptItem]:
    """Return accepted goods receipts that have not yet been matched to supplier invoices."""
    grn_items = (
        GoodsReceiptItem.objects.filter(
            goods_receipt__organization_id=organization_id,
            quantity_accepted__gt=0,
            is_inspected=True,
        )
        .select_related("goods_receipt", "po_item")
        .prefetch_related("po_item__allocations__requisition_item")
        .order_by("-goods_receipt__received_date")
    )

    results: list[AcceptedReceiptItem] = []
    for ri in grn_items[offset : offset + limit]:
        alloc = ri.po_item.allocations.first()
        prog_id = alloc.requisition_item.program_id if alloc and alloc.requisition_item else None
        qty_acc = Decimal(str(ri.quantity_accepted))
        unit_p = Decimal(str(ri.po_item.unit_price))
        results.append(
            AcceptedReceiptItem(
                grn_id=ri.goods_receipt_id,
                receipt_number=ri.goods_receipt.receipt_number,
                po_item_id=ri.po_item_id,
                description=ri.po_item.description,
                quantity_accepted=qty_acc,
                unit_price=unit_p,
                accepted_value=qty_acc * unit_p,
                received_date=ri.goods_receipt.received_date,
                program_id=prog_id,
            )
        )
    return results


__all__ = [
    "AcceptedReceiptItem",
    "AuthorizationStatus",
    "GoodsReceiptNotFoundError",
    "ProcurementCommitmentItem",
    "ProcurementCommitmentSummary",
    "ProcurementError",
    "PurchaseOrderNotFoundError",
    "PurchaseOrderStatus",
    "ReceiptType",
    "RequisitionNotFoundError",
    "VendorNotFoundError",
    "VendorType",
    "VendorVerificationStatus",
    "get_accepted_receipts_for_order",
    "get_commitment_detail",
    "get_outstanding_commitments",
    "get_unmatched_accepted_receipts",
]
