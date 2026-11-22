"""Exceptions for the Inventory domain."""

from __future__ import annotations

from abren_one.platform.common.exceptions import DomainError, NotFoundError


class InventoryError(DomainError):
    """Base exception for all domain errors in Inventory."""


class ItemNotFoundError(NotFoundError, InventoryError):
    """Raised when an inventory item is not found in the current organization."""


class CategoryNotFoundError(NotFoundError, InventoryError):
    """Raised when an item category is not found in the current organization."""


class WarehouseNotFoundError(NotFoundError, InventoryError):
    """Raised when a warehouse is not found in the current organization."""


class LocationNotFoundError(NotFoundError, InventoryError):
    """Raised when a storage location is not found in the specified warehouse."""


class BatchNotFoundError(NotFoundError, InventoryError):
    """Raised when an item batch is not found."""


class TransactionNotFoundError(NotFoundError, InventoryError):
    """Raised when a stock transaction is not found in the current organization."""


class OrganizationMismatchError(InventoryError):
    """Raised when related inventory entities belong to different organizations."""


class InsufficientStockError(InventoryError):
    """Raised when attempting to issue or transfer more stock than is currently available."""


class ImmutableStockTransactionError(InventoryError):
    """Raised when attempting to modify or delete a posted stock transaction or ledger entry."""


class InactiveItemError(InventoryError):
    """Raised when an operation targets an inactive item."""


class InactiveWarehouseError(InventoryError):
    """Raised when an operation targets an inactive warehouse."""


class ExpiredStockIssueError(InventoryError):
    """Raised when attempting to issue an expired item batch without authorized disposal."""


class InvalidBatchRequirementError(InventoryError):
    """Raised when a batch is required for a batch-tracked item but not provided, or vice-versa."""


class SameWarehouseTransferError(InventoryError):
    """Raised when source and destination warehouse are identical in a transfer."""
