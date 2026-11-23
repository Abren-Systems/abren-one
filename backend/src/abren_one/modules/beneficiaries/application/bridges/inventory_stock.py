"""Beneficiaries → Inventory Bridge (ADR-006).

Connects humanitarian service deliveries (e.g. food rations, hygiene kits,
medical supplies) to warehouse stock issues.

When aid is delivered to a beneficiary from inventory stock:
1. Verifies stock availability and batch validity (including expiry checks).
2. Issues the stock out of the warehouse, recording immutable ledger movements.
3. Automatically posts GL entries to Finance via the inventory GL bridge.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.inventory.public import (
    IssueLineInput,
    IssueStockInput,
    issue_stock,
)
from abren_one.platform.common.context import ExecutionContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AidStockIssueResult:
    """Result of issuing stock for a service delivery."""

    transaction_id: UUID
    transaction_number: str
    total_quantity_issued: Decimal


def issue_stock_for_service_delivery(
    *,
    context: ExecutionContext,
    delivery_id: UUID,
    warehouse_id: UUID,
    item_id: UUID,
    quantity: Decimal,
    delivery_date: date,
    beneficiary_name: str,
    service_type: str,
    batch_id: UUID | None = None,
    location_id: UUID | None = None,
    program_id: UUID | None = None,
    activity_id: UUID | None = None,
    notes: str = "",
) -> AidStockIssueResult:
    """Issue inventory relief goods for a beneficiary service delivery.

    Enforces batch validity, expiry dates, and warehouse balance checks.
    Automatically generates GL postings: Dr 5100 Program Relief Exp, Cr 1200 Inventory Asset.
    """
    ref_doc = f"DELIVERY-{delivery_id}"
    memo_notes = f"Aid distribution ({service_type}) to {beneficiary_name}"
    if notes.strip():
        memo_notes = f"{memo_notes}: {notes.strip()}"

    issue_input = IssueStockInput(
        context=context,
        warehouse_id=warehouse_id,
        transaction_date=delivery_date,
        is_program_issue=True,
        recipient_name=beneficiary_name,
        reference_document=ref_doc,
        notes=memo_notes,
        lines=[
            IssueLineInput(
                item_id=item_id,
                quantity=quantity,
                batch_id=batch_id,
                location_id=location_id,
                program_id=program_id,
                activity_id=activity_id,
            )
        ],
    )

    result = issue_stock(issue_input)

    logger.info(
        "Aid distribution bridge: issued %s units of item %s from warehouse %s (txn: %s) for delivery %s to %s.",
        quantity,
        item_id,
        warehouse_id,
        result.transaction_number,
        delivery_id,
        beneficiary_name,
    )

    return AidStockIssueResult(
        transaction_id=result.transaction_id,
        transaction_number=result.transaction_number,
        total_quantity_issued=result.total_quantity_issued,
    )
