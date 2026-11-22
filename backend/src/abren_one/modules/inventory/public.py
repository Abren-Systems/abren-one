"""Public interface for the Inventory module.

Other modules must import ONLY from this file.
Cross-module ForeignKeys use string references ("inventory.Item", "inventory.Warehouse").
"""

from abren_one.modules.inventory.application.queries.check_item_availability import (
    ItemAvailabilityResult,
)
from abren_one.modules.inventory.application.queries.check_item_availability import (
    execute as check_item_availability,
)
from abren_one.modules.inventory.application.queries.get_expiring_batches import (
    ExpiringBatchAlertResult,
)
from abren_one.modules.inventory.application.queries.get_expiring_batches import (
    execute as get_expiring_batches,
)
from abren_one.modules.inventory.application.queries.get_reorder_alerts import (
    ReorderAlertResult,
)
from abren_one.modules.inventory.application.queries.get_reorder_alerts import (
    execute as get_reorder_alerts,
)
from abren_one.modules.inventory.application.queries.get_stock_balances import (
    StockBalanceItemResult,
)
from abren_one.modules.inventory.application.queries.get_stock_balances import (
    execute as get_stock_balances,
)
from abren_one.modules.inventory.domain.exceptions import (
    BatchNotFoundError,
    CategoryNotFoundError,
    ExpiredStockIssueError,
    ImmutableStockTransactionError,
    InactiveItemError,
    InactiveWarehouseError,
    InsufficientStockError,
    InvalidBatchRequirementError,
    InventoryError,
    ItemNotFoundError,
    LocationNotFoundError,
    OrganizationMismatchError,
    SameWarehouseTransferError,
    TransactionNotFoundError,
    WarehouseNotFoundError,
)

__all__ = [
    # Domain Exceptions
    "BatchNotFoundError",
    "CategoryNotFoundError",
    "ExpiredStockIssueError",
    "ImmutableStockTransactionError",
    "InactiveItemError",
    "InactiveWarehouseError",
    "InsufficientStockError",
    "InvalidBatchRequirementError",
    "InventoryError",
    "ItemNotFoundError",
    "LocationNotFoundError",
    "OrganizationMismatchError",
    "SameWarehouseTransferError",
    "TransactionNotFoundError",
    "WarehouseNotFoundError",
    # Public Query DTOs & Functions
    "ExpiringBatchAlertResult",
    "ItemAvailabilityResult",
    "ReorderAlertResult",
    "StockBalanceItemResult",
    "check_item_availability",
    "get_expiring_batches",
    "get_reorder_alerts",
    "get_stock_balances",
]
