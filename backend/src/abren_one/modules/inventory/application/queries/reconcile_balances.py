"""Query service to audit and reconcile materialized stock balances against the immutable ledger."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db.models import Sum

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import StockBalance, StockLedgerEntry
from abren_one.platform.authorization.evaluator import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class BalanceDiscrepancyResult:
    warehouse_id: UUID
    warehouse_name: str
    item_id: UUID
    item_name: str
    location_id: UUID | None
    batch_id: UUID | None
    materialized_quantity: Decimal
    ledger_sum_quantity: Decimal
    difference: Decimal


@dataclass(frozen=True)
class ReconciliationReportResult:
    total_balances_checked: int
    discrepancies_count: int
    is_healthy: bool
    discrepancies: list[BalanceDiscrepancyResult]


def execute(
    context: ExecutionContext,
    warehouse_id: UUID | None = None,
    item_id: UUID | None = None,
) -> ReconciliationReportResult:
    """Audit materialized stock balance projections against the immutable ledger.

    Every balance row's quantity_on_hand must strictly equal the algebraic sum
    of its corresponding stock ledger entries.
    """
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    check_permission(context, "inventory:stock:view")

    balances_qs = StockBalance.objects.filter(organization_id=context.organization_id).select_related(
        "item", "warehouse", "location", "batch"
    )
    if warehouse_id:
        balances_qs = balances_qs.filter(warehouse_id=warehouse_id)
    if item_id:
        balances_qs = balances_qs.filter(item_id=item_id)

    discrepancies: list[BalanceDiscrepancyResult] = []
    checked_count = 0

    for balance in balances_qs:
        checked_count += 1
        ledger_filter = {
            "organization_id": context.organization_id,
            "warehouse_id": balance.warehouse_id,
            "item_id": balance.item_id,
        }
        if balance.location_id:
            ledger_filter["location_id"] = balance.location_id
        else:
            ledger_filter["location__isnull"] = True

        if balance.batch_id:
            ledger_filter["batch_id"] = balance.batch_id
        else:
            ledger_filter["batch__isnull"] = True

        ledger_sum = StockLedgerEntry.objects.filter(**ledger_filter).aggregate(total=Sum("quantity"))[
            "total"
        ] or Decimal("0.00")

        if balance.quantity_on_hand != ledger_sum:
            discrepancies.append(
                BalanceDiscrepancyResult(
                    warehouse_id=balance.warehouse_id,
                    warehouse_name=balance.warehouse.name,
                    item_id=balance.item_id,
                    item_name=balance.item.name,
                    location_id=balance.location_id,
                    batch_id=balance.batch_id,
                    materialized_quantity=balance.quantity_on_hand,
                    ledger_sum_quantity=ledger_sum,
                    difference=balance.quantity_on_hand - ledger_sum,
                )
            )

    return ReconciliationReportResult(
        total_balances_checked=checked_count,
        discrepancies_count=len(discrepancies),
        is_healthy=len(discrepancies) == 0,
        discrepancies=discrepancies,
    )
