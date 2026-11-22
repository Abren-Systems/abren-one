"""Pure Python domain policies and invariants for the Inventory module.

Independent of ORM, database, and transport layers.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import (
    ExpiredStockIssueError,
    InactiveItemError,
    InactiveWarehouseError,
    InsufficientStockError,
    InvalidBatchRequirementError,
    InventoryError,
    SameWarehouseTransferError,
)


def validate_item_active(is_active: bool) -> None:
    """Ensure an item is active before performing movements."""
    if not is_active:
        raise InactiveItemError("Cannot perform stock operations for an inactive item.")


def validate_warehouse_active(is_active: bool) -> None:
    """Ensure a warehouse is active before performing movements."""
    if not is_active:
        raise InactiveWarehouseError("Cannot perform stock operations for an inactive warehouse.")


def validate_batch_requirement(track_batches: bool, has_batch: bool) -> None:
    """Ensure batch is specified if and only if item is configured to track batches."""
    if track_batches and not has_batch:
        raise InvalidBatchRequirementError("Batch identification is required for this batch-tracked item.")


def validate_batch_not_expired(
    track_expiry: bool,
    expiry_date: date | None,
    transaction_date: date,
    *,
    is_disposal: bool = False,
) -> None:
    """Prevent issuing expired inventory to programs or beneficiaries."""
    if is_disposal:
        return
    if track_expiry and expiry_date is not None and expiry_date < transaction_date:
        raise ExpiredStockIssueError(
            f"Cannot issue expired batch (expired on {expiry_date.isoformat()}). "
            "Expired stock must be processed through an authorized write-off disposal."
        )


def validate_sufficient_stock(quantity_available: Decimal, requested_quantity: Decimal) -> None:
    """Prevent overselling or issuing unavailable stock."""
    if requested_quantity <= Decimal("0"):
        raise InventoryError("Issue quantity must be greater than zero.")
    if requested_quantity > quantity_available:
        raise InsufficientStockError(
            f"Insufficient available stock ({quantity_available}). Cannot issue {requested_quantity}."
        )


def validate_different_warehouses(source_warehouse_id: UUID, destination_warehouse_id: UUID) -> None:
    """Ensure inter-warehouse transfer connects two distinct facilities."""
    if source_warehouse_id == destination_warehouse_id:
        raise SameWarehouseTransferError("Source and destination warehouse cannot be the same for a transfer.")


def validate_positive_quantity(quantity: Decimal, field_name: str = "Quantity") -> None:
    """Ensure quantity is strictly positive."""
    if quantity <= Decimal("0"):
        raise InventoryError(f"{field_name} must be greater than zero.")


def validate_non_negative(value: Decimal, field_name: str = "Value") -> None:
    """Ensure value is non-negative."""
    if value < Decimal("0"):
        raise InventoryError(f"{field_name} cannot be negative.")
