"""Value objects and enumerations for the Inventory domain."""

from enum import StrEnum


class ItemType(StrEnum):
    """Classification of inventory items."""

    CONSUMABLE = "consumable"
    DURABLE_ASSET = "durable_asset"
    RELIEF_GOOD = "relief_good"


class WarehouseType(StrEnum):
    """Classification of physical stock-holding facilities."""

    CENTRAL = "central"
    REGIONAL_DEPOT = "regional_depot"
    FIELD_DISPENSARY = "field_dispensary"
    TRANSIT = "transit"


class TransactionType(StrEnum):
    """Types of inventory movement transactions."""

    RECEIPT_OPENING = "receipt_opening"
    RECEIPT_DONATION = "receipt_donation"
    TRANSFER = "transfer"
    ISSUE_GENERAL = "issue_general"
    ISSUE_PROGRAM = "issue_program"
    ADJUSTMENT_COUNT = "adjustment_count"
    WRITE_OFF_DISPOSAL = "write_off_disposal"


class TransactionStatus(StrEnum):
    """Lifecycle status of a stock movement transaction."""

    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"
