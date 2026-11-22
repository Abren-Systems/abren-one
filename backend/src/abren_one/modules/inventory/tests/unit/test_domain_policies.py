"""Unit tests for Inventory domain policies and value objects."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from abren_one.modules.inventory.domain.exceptions import (
    ExpiredStockIssueError,
    InactiveItemError,
    InactiveWarehouseError,
    InsufficientStockError,
    InvalidBatchRequirementError,
    InventoryError,
    SameWarehouseTransferError,
)
from abren_one.modules.inventory.domain.policies import (
    validate_batch_not_expired,
    validate_batch_requirement,
    validate_different_warehouses,
    validate_item_active,
    validate_non_negative,
    validate_positive_quantity,
    validate_sufficient_stock,
    validate_warehouse_active,
)
from abren_one.modules.inventory.domain.value_objects import (
    ItemType,
    TransactionStatus,
    TransactionType,
    WarehouseType,
)


class TestValueObjects:
    def test_item_types(self):
        assert ItemType.CONSUMABLE == "consumable"
        assert ItemType.DURABLE_ASSET == "durable_asset"
        assert ItemType.RELIEF_GOOD == "relief_good"

    def test_warehouse_types(self):
        assert WarehouseType.CENTRAL == "central"
        assert WarehouseType.REGIONAL_DEPOT == "regional_depot"
        assert WarehouseType.FIELD_DISPENSARY == "field_dispensary"
        assert WarehouseType.TRANSIT == "transit"

    def test_transaction_types(self):
        assert TransactionType.RECEIPT_OPENING == "receipt_opening"
        assert TransactionType.RECEIPT_DONATION == "receipt_donation"
        assert TransactionType.TRANSFER == "transfer"
        assert TransactionType.ISSUE_GENERAL == "issue_general"
        assert TransactionType.ISSUE_PROGRAM == "issue_program"
        assert TransactionType.ADJUSTMENT_COUNT == "adjustment_count"
        assert TransactionType.WRITE_OFF_DISPOSAL == "write_off_disposal"

    def test_transaction_statuses(self):
        assert TransactionStatus.DRAFT == "draft"
        assert TransactionStatus.POSTED == "posted"
        assert TransactionStatus.CANCELLED == "cancelled"


class TestDomainPolicies:
    def test_item_active_validation(self):
        validate_item_active(True)
        with pytest.raises(InactiveItemError):
            validate_item_active(False)

    def test_warehouse_active_validation(self):
        validate_warehouse_active(True)
        with pytest.raises(InactiveWarehouseError):
            validate_warehouse_active(False)

    def test_batch_requirement_validation(self):
        # Non-tracked item: no batch required
        validate_batch_requirement(track_batches=False, has_batch=False)
        validate_batch_requirement(track_batches=False, has_batch=True)

        # Batch-tracked item: batch is mandatory
        validate_batch_requirement(track_batches=True, has_batch=True)
        with pytest.raises(InvalidBatchRequirementError):
            validate_batch_requirement(track_batches=True, has_batch=False)

    def test_batch_expiry_validation(self):
        today = date.today()
        future = today + timedelta(days=90)
        past = today - timedelta(days=10)

        # Non-expiry tracked item passes regardless of date
        validate_batch_not_expired(track_expiry=False, expiry_date=past, transaction_date=today)

        # Active future expiry passes
        validate_batch_not_expired(track_expiry=True, expiry_date=future, transaction_date=today)

        # Expired batch raises ExpiredStockIssueError
        with pytest.raises(ExpiredStockIssueError, match="Cannot issue expired batch"):
            validate_batch_not_expired(track_expiry=True, expiry_date=past, transaction_date=today)

        # Disposal write-off allows expired stock
        validate_batch_not_expired(
            track_expiry=True,
            expiry_date=past,
            transaction_date=today,
            is_disposal=True,
        )

    def test_sufficient_stock_validation(self):
        # Available 50, issue 30 -> OK
        validate_sufficient_stock(Decimal("50.00"), Decimal("30.00"))
        # Available 50, issue 50 -> OK
        validate_sufficient_stock(Decimal("50.00"), Decimal("50.00"))

        # Available 50, issue 51 -> InsufficientStockError
        with pytest.raises(InsufficientStockError):
            validate_sufficient_stock(Decimal("50.00"), Decimal("50.01"))

        # Zero or negative issue quantity raises InventoryError
        with pytest.raises(InventoryError):
            validate_sufficient_stock(Decimal("50.00"), Decimal("0.00"))
        with pytest.raises(InventoryError):
            validate_sufficient_stock(Decimal("50.00"), Decimal("-5.00"))

    def test_different_warehouses_validation(self):
        wh_a = uuid.uuid4()
        wh_b = uuid.uuid4()
        validate_different_warehouses(wh_a, wh_b)

        with pytest.raises(SameWarehouseTransferError):
            validate_different_warehouses(wh_a, wh_a)

    def test_positive_quantity_validation(self):
        validate_positive_quantity(Decimal("10.50"))
        with pytest.raises(InventoryError):
            validate_positive_quantity(Decimal("0.00"))
        with pytest.raises(InventoryError):
            validate_positive_quantity(Decimal("-1.00"))

    def test_non_negative_validation(self):
        validate_non_negative(Decimal("0.00"))
        validate_non_negative(Decimal("15.00"))
        with pytest.raises(InventoryError):
            validate_non_negative(Decimal("-0.01"))
