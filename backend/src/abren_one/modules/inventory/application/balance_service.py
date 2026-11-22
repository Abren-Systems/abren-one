"""Stock balance posting and mutation service."""

from decimal import Decimal
from typing import NamedTuple
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import InsufficientStockError
from abren_one.modules.inventory.domain.policies import validate_sufficient_stock
from abren_one.modules.inventory.models import (
    Item,
    ItemBatch,
    StockBalance,
    StockLedgerEntry,
    StockTransaction,
    StorageLocation,
    Warehouse,
)


class LedgerPostingLine(NamedTuple):
    item: Item
    warehouse: Warehouse
    location: StorageLocation | None
    batch: ItemBatch | None
    quantity: Decimal
    unit_cost: Decimal = Decimal("0.00")
    program_id: UUID | None = None
    activity_id: UUID | None = None


def post_ledger_entries(
    stock_transaction: StockTransaction,
    lines: list[LedgerPostingLine],
) -> list[StockLedgerEntry]:
    """Atomically record immutable ledger entries and update corresponding stock balances.

    Locks stock balances in a deterministic order to prevent concurrent deadlocks.
    Validates available stock and enforces non-negative operational balance constraints.
    """
    with transaction.atomic():
        org_id = stock_transaction.organization_id

        # Sort entries by unique key components to prevent database lock inversion deadlocks
        sorted_lines = sorted(
            lines,
            key=lambda line: (
                line.warehouse.id,
                line.item.id,
                line.location.id if line.location else UUID(int=0),
                line.batch.id if line.batch else UUID(int=0),
            ),
        )

        created_entries: list[StockLedgerEntry] = []

        for line in sorted_lines:
            # Fetch or create balance with row locking
            balance_qs = StockBalance.objects.select_for_update().filter(
                organization_id=org_id,
                warehouse=line.warehouse,
                location=line.location,
                item=line.item,
                batch=line.batch,
            )
            balance = balance_qs.first()

            if balance is None:
                if line.quantity < 0:
                    raise InsufficientStockError(
                        f"Insufficient stock for {line.item.name}: available 0.00, requested {-line.quantity:.2f}"
                    )
                balance = StockBalance.objects.create(
                    organization_id=org_id,
                    warehouse=line.warehouse,
                    location=line.location,
                    item=line.item,
                    batch=line.batch,
                    quantity_on_hand=Decimal("0.00"),
                    quantity_reserved=Decimal("0.00"),
                )

            if line.quantity < 0:
                validate_sufficient_stock(
                    quantity_available=balance.available_quantity,
                    requested_quantity=-line.quantity,
                )

            # Update balance
            balance.quantity_on_hand += line.quantity
            balance.save()

            # Create immutable ledger entry
            entry = StockLedgerEntry.objects.create(
                organization_id=org_id,
                transaction=stock_transaction,
                item=line.item,
                batch=line.batch,
                warehouse=line.warehouse,
                location=line.location,
                quantity=line.quantity,
                unit_cost=line.unit_cost,
                program_id=line.program_id,
                activity_id=line.activity_id,
            )
            created_entries.append(entry)

        return created_entries
