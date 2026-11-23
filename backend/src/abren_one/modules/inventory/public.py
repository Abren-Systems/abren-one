"""Public interface for the Inventory module.

Other modules must import ONLY from this file.
Cross-module ForeignKeys use string references ("inventory.Item", "inventory.Warehouse").
"""

from abren_one.modules.inventory.application.commands.adjust_stock import (
    AdjustmentLineInput,
    AdjustStockInput,
    AdjustStockResult,
)
from abren_one.modules.inventory.application.commands.adjust_stock import (
    execute as adjust_stock,
)
from abren_one.modules.inventory.application.commands.create_item import (
    CreateItemInput,
    CreateItemResult,
)
from abren_one.modules.inventory.application.commands.create_item import (
    execute as create_item,
)
from abren_one.modules.inventory.application.commands.create_item_batch import (
    CreateItemBatchInput,
    CreateItemBatchResult,
)
from abren_one.modules.inventory.application.commands.create_item_batch import (
    execute as create_item_batch,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    CreateItemCategoryInput,
    CreateItemCategoryResult,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    execute as create_item_category,
)
from abren_one.modules.inventory.application.commands.create_storage_location import (
    CreateStorageLocationInput,
    CreateStorageLocationResult,
)
from abren_one.modules.inventory.application.commands.create_storage_location import (
    execute as create_storage_location,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    CreateWarehouseInput,
    CreateWarehouseResult,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    execute as create_warehouse,
)
from abren_one.modules.inventory.application.commands.issue_stock import (
    IssueLineInput,
    IssueStockInput,
    IssueStockResult,
)
from abren_one.modules.inventory.application.commands.issue_stock import (
    execute as issue_stock,
)
from abren_one.modules.inventory.application.commands.receive_in_kind_donation import (
    DonationReceiptLineInput,
    DonationReceiptResult,
    ReceiveDonationInput,
)
from abren_one.modules.inventory.application.commands.receive_in_kind_donation import (
    execute as receive_in_kind_donation,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    OpeningStockLineInput,
    ReceiveOpeningStockInput,
    StockReceiptResult,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    execute as receive_opening_stock,
)
from abren_one.modules.inventory.application.commands.receive_purchased_stock import (
    ReceivePurchasedStockInput,
    ReceivePurchasedStockLineInput,
    ReceivePurchasedStockResult,
)
from abren_one.modules.inventory.application.commands.receive_purchased_stock import (
    execute as receive_purchased_stock,
)
from abren_one.modules.inventory.application.commands.transfer_stock import (
    TransferLineInput,
    TransferStockInput,
    TransferStockResult,
)
from abren_one.modules.inventory.application.commands.transfer_stock import (
    execute as transfer_stock,
)
from abren_one.modules.inventory.application.commands.write_off_stock import (
    WriteOffLineInput,
    WriteOffStockInput,
    WriteOffStockResult,
)
from abren_one.modules.inventory.application.commands.write_off_stock import (
    execute as write_off_stock,
)
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
from abren_one.modules.inventory.application.queries.get_stock_ledger import (
    StockLedgerEntryResult,
)
from abren_one.modules.inventory.application.queries.get_stock_ledger import (
    execute as get_stock_ledger,
)
from abren_one.modules.inventory.application.queries.get_transaction_detail import (
    StockTransactionDetailResult,
    TransactionEntryLineResult,
)
from abren_one.modules.inventory.application.queries.get_transaction_detail import (
    execute as get_transaction_detail,
)
from abren_one.modules.inventory.application.queries.list_pending_grns import (
    PendingGRNItemResult,
    PendingGRNResult,
)
from abren_one.modules.inventory.application.queries.list_pending_grns import (
    execute as list_pending_grns,
)
from abren_one.modules.inventory.application.queries.reconcile_balances import (
    BalanceDiscrepancyResult,
    ReconciliationReportResult,
)
from abren_one.modules.inventory.application.queries.reconcile_balances import (
    execute as reconcile_balances,
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
from abren_one.modules.inventory.domain.value_objects import (
    ItemType,
    TransactionStatus,
    TransactionType,
    WarehouseType,
)

__all__ = [
    # Domain Value Objects & Enums
    "ItemType",
    "TransactionStatus",
    "TransactionType",
    "WarehouseType",
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
    # Master Data Commands & DTOs
    "CreateItemBatchInput",
    "CreateItemBatchResult",
    "CreateItemCategoryInput",
    "CreateItemCategoryResult",
    "CreateItemInput",
    "CreateItemResult",
    "CreateStorageLocationInput",
    "CreateStorageLocationResult",
    "CreateWarehouseInput",
    "CreateWarehouseResult",
    "create_item",
    "create_item_batch",
    "create_item_category",
    "create_storage_location",
    "create_warehouse",
    # Movement Commands & DTOs
    "AdjustStockInput",
    "AdjustStockResult",
    "AdjustmentLineInput",
    "DonationReceiptLineInput",
    "DonationReceiptResult",
    "IssueLineInput",
    "IssueStockInput",
    "IssueStockResult",
    "OpeningStockLineInput",
    "ReceiveDonationInput",
    "ReceiveOpeningStockInput",
    "ReceivePurchasedStockInput",
    "ReceivePurchasedStockLineInput",
    "ReceivePurchasedStockResult",
    "StockReceiptResult",
    "TransferLineInput",
    "TransferStockInput",
    "TransferStockResult",
    "WriteOffLineInput",
    "WriteOffStockInput",
    "WriteOffStockResult",
    "adjust_stock",
    "issue_stock",
    "receive_in_kind_donation",
    "receive_opening_stock",
    "receive_purchased_stock",
    "transfer_stock",
    "write_off_stock",
    # Queries & DTOs
    "BalanceDiscrepancyResult",
    "ExpiringBatchAlertResult",
    "ItemAvailabilityResult",
    "PendingGRNItemResult",
    "PendingGRNResult",
    "ReconciliationReportResult",
    "ReorderAlertResult",
    "StockBalanceItemResult",
    "StockLedgerEntryResult",
    "StockTransactionDetailResult",
    "TransactionEntryLineResult",
    "check_item_availability",
    "get_expiring_batches",
    "get_reorder_alerts",
    "get_stock_balances",
    "get_stock_ledger",
    "get_transaction_detail",
    "list_pending_grns",
    "reconcile_balances",
]
