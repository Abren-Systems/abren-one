"""Query to list procurement goods receipts available for inventory intake."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import models

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import StockLedgerEntry
from abren_one.modules.procurement.public import list_inspected_goods_receipts
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class PendingGRNItemResult:
    grn_item_id: UUID
    po_item_id: UUID
    description: str
    quantity_received: Decimal
    quantity_accepted: Decimal
    quantity_already_received: Decimal
    quantity_remaining: Decimal
    unit: str
    unit_price: Decimal


@dataclass(frozen=True)
class PendingGRNResult:
    grn_id: UUID
    receipt_number: str
    purchase_order_id: UUID
    purchase_order_number: str
    vendor_name: str
    received_date: date
    total_items: int
    items: list[PendingGRNItemResult]


def execute(
    context: ExecutionContext,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[PendingGRNResult]:
    """List inspected goods receipts that have accepted items not yet fully received into inventory."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(context, "inventory:stock:view")

    grns = list_inspected_goods_receipts(
        context.organization_id,
        receipt_type="goods",
        limit=limit,
        offset=offset,
    )

    results: list[PendingGRNResult] = []

    for grn in grns:
        pending_items: list[PendingGRNItemResult] = []

        for item in grn.items:
            if not item.is_inspected or item.quantity_accepted <= Decimal("0.00"):
                continue

            already_received = StockLedgerEntry.objects.filter(
                transaction__goods_receipt_id=grn.grn_id,
                po_item_id=item.po_item_id,
                quantity__gt=0,
            ).aggregate(total=models.Sum("quantity"))["total"] or Decimal("0.00")

            already_recv_dec = Decimal(str(already_received))
            remaining = max(Decimal("0.00"), item.quantity_accepted - already_recv_dec)

            if remaining > Decimal("0.00"):
                pending_items.append(
                    PendingGRNItemResult(
                        grn_item_id=item.grn_item_id,
                        po_item_id=item.po_item_id,
                        description=item.description,
                        quantity_received=item.quantity_received,
                        quantity_accepted=item.quantity_accepted,
                        quantity_already_received=already_recv_dec,
                        quantity_remaining=remaining,
                        unit=item.unit,
                        unit_price=item.unit_price,
                    )
                )

        if pending_items:
            results.append(
                PendingGRNResult(
                    grn_id=grn.grn_id,
                    receipt_number=grn.receipt_number,
                    purchase_order_id=grn.purchase_order_id,
                    purchase_order_number=grn.purchase_order_number,
                    vendor_name=grn.vendor_name,
                    received_date=grn.received_date,
                    total_items=len(pending_items),
                    items=pending_items,
                )
            )

    return results
