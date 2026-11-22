from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction

from abren_one.modules.inventory.application.commands.create_item import (
    CreateItemInput,
)
from abren_one.modules.inventory.application.commands.create_item import (
    execute as create_item,
)
from abren_one.modules.inventory.application.commands.create_item_batch import (
    CreateItemBatchInput,
)
from abren_one.modules.inventory.application.commands.create_item_batch import (
    execute as create_item_batch,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    CreateItemCategoryInput,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    execute as create_item_category,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    CreateWarehouseInput,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    execute as create_warehouse,
)
from abren_one.modules.inventory.application.commands.receive_in_kind_donation import (
    DonationReceiptLineInput,
    ReceiveDonationInput,
)
from abren_one.modules.inventory.application.commands.receive_in_kind_donation import (
    execute as receive_in_kind_donation,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    OpeningStockLineInput,
    ReceiveOpeningStockInput,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    execute as receive_opening_stock,
)
from abren_one.modules.inventory.application.queries.get_stock_balances import (
    execute as get_stock_balances,
)
from abren_one.modules.inventory.application.queries.get_stock_ledger import (
    execute as get_stock_ledger,
)
from abren_one.modules.inventory.application.queries.get_transaction_detail import (
    execute as get_transaction_detail,
)
from abren_one.modules.inventory.application.queries.reconcile_balances import (
    execute as reconcile_balances,
)
from abren_one.modules.inventory.domain.exceptions import (
    ImmutableStockTransactionError,
    InactiveItemError,
    InactiveWarehouseError,
    InvalidBatchRequirementError,
)
from abren_one.modules.inventory.models import (
    Item,
    StockBalance,
    StockLedgerEntry,
    StockTransaction,
    Warehouse,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestPhase2StockLedger:
    @pytest.fixture(autouse=True)
    def setup_fixtures(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid4(),
        )
        org_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Relief Org Global",
                slug=f"relief-org-{uuid4().hex[:6]}",
            )
        )
        self.org_id = org_res.organization_id
        self.admin_user_id = uuid4()
        self.member_user_id = uuid4()

        self.admin_ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=self.admin_user_id,
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )
        self.member_ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=self.member_user_id,
            actor_role=Role.MEMBER.value,
            correlation_id=uuid4(),
        )

        cat_res = create_item_category(
            CreateItemCategoryInput(context=self.admin_ctx, name="Medical Supplies", code="MED-SUP")
        )
        self.category_id = cat_res.category_id

        item_res = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="MED-BAND-01",
                name="Sterile Gauze Bandages",
                unit_of_measure="boxes",
                reorder_threshold=Decimal("50.00"),
                default_unit_cost=Decimal("2.50"),
            )
        )
        self.item_id = item_res.item_id

        # Batch-tracked item
        batch_item_res = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="MED-AMOX-500",
                name="Amoxicillin 500mg Capsules",
                unit_of_measure="bottles",
                track_batches=True,
                track_expiry=True,
            )
        )
        self.batch_item_id = batch_item_res.item_id

        batch_res = create_item_batch(
            CreateItemBatchInput(
                context=self.admin_ctx,
                item_id=self.batch_item_id,
                batch_number="LOT-AMOX-2026A",
                expiry_date=date(2027, 6, 30),
            )
        )
        self.batch_id = batch_res.batch_id

        wh_res = create_warehouse(
            CreateWarehouseInput(
                context=self.admin_ctx,
                name="Central Depo Addis",
                code="WH-ADDIS",
            )
        )
        self.warehouse_id = wh_res.warehouse_id

    def test_receive_opening_stock_lifecycle(self) -> None:
        """Opening stock intake creates transaction, signed entries, and updates balances."""
        res = receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse_id,
                transaction_date=date(2026, 11, 20),
                reference_document="INV-INIT-2026",
                notes="Initial physical count intake",
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("150.00"),
                        unit_cost=Decimal("2.50"),
                    ),
                    OpeningStockLineInput(
                        item_id=self.batch_item_id,
                        quantity=Decimal("300.00"),
                        unit_cost=Decimal("12.00"),
                        batch_id=self.batch_id,
                    ),
                ],
            )
        )

        assert res.total_lines == 2
        assert res.total_quantity == Decimal("450.00")
        assert res.transaction_number.startswith("TXN-")

        # Verify balances
        balances = get_stock_balances(self.admin_ctx, warehouse_id=self.warehouse_id)
        assert len(balances) == 2
        b1 = next(b for b in balances if b.item_id == self.item_id)
        assert b1.quantity_on_hand == Decimal("150.00")
        assert b1.available_quantity == Decimal("150.00")
        assert not b1.is_low_stock

        b2 = next(b for b in balances if b.item_id == self.batch_item_id)
        assert b2.quantity_on_hand == Decimal("300.00")
        assert b2.batch_number == "LOT-AMOX-2026A"

        # Verify ledger entries
        ledger = get_stock_ledger(self.admin_ctx, warehouse_id=self.warehouse_id)
        assert len(ledger) == 2
        assert all(entry.quantity > 0 for entry in ledger)

        # Verify audit trail
        audit_events = AuditEvent.objects.filter(
            organization_id=self.org_id,
            action="inventory.stock.opening_received",
        )
        assert audit_events.exists()

        # Reconcile balances
        rec = reconcile_balances(self.admin_ctx)
        assert rec.is_healthy
        assert rec.discrepancies_count == 0

    def test_receive_in_kind_donation_lifecycle(self) -> None:
        """In-kind donation records donor name and emits positive ledger movements."""
        res = receive_in_kind_donation(
            ReceiveDonationInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse_id,
                donor_name="Global Health Foundation",
                transaction_date=date(2026, 11, 21),
                reference_document="DON-GHF-998",
                lines=[
                    DonationReceiptLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("50.00"),
                        unit_cost=Decimal("2.40"),
                    )
                ],
            )
        )

        assert res.donor_name == "Global Health Foundation"
        assert res.total_quantity == Decimal("50.00")

        # Get transaction detail query
        txn_detail = get_transaction_detail(self.admin_ctx, transaction_id=res.transaction_id)
        assert txn_detail.donor_name == "Global Health Foundation"
        assert len(txn_detail.entries) == 1
        assert txn_detail.entries[0].quantity == Decimal("50.00")

    def test_batch_validation_on_receipt(self) -> None:
        """Batch-tracked items require a valid batch on receipt."""
        with pytest.raises(InvalidBatchRequirementError):
            receive_opening_stock(
                ReceiveOpeningStockInput(
                    context=self.admin_ctx,
                    warehouse_id=self.warehouse_id,
                    transaction_date=date(2026, 11, 20),
                    lines=[
                        OpeningStockLineInput(
                            item_id=self.batch_item_id,
                            quantity=Decimal("10.00"),
                            batch_id=None,  # Missing batch on batch-tracked item
                        )
                    ],
                )
            )

    def test_inactive_item_or_warehouse_rejected(self) -> None:
        """Receipt into inactive warehouse or inactive item is rejected."""
        # Deactivate item
        item = Item.objects.get(id=self.item_id)
        item.is_active = False
        item.save()

        with pytest.raises(InactiveItemError):
            receive_opening_stock(
                ReceiveOpeningStockInput(
                    context=self.admin_ctx,
                    warehouse_id=self.warehouse_id,
                    transaction_date=date(2026, 11, 20),
                    lines=[
                        OpeningStockLineInput(
                            item_id=self.item_id,
                            quantity=Decimal("10.00"),
                        )
                    ],
                )
            )

        item.is_active = True
        item.save()

        # Deactivate warehouse
        wh = Warehouse.objects.get(id=self.warehouse_id)
        wh.is_active = False
        wh.save()

        with pytest.raises(InactiveWarehouseError):
            receive_opening_stock(
                ReceiveOpeningStockInput(
                    context=self.admin_ctx,
                    warehouse_id=self.warehouse_id,
                    transaction_date=date(2026, 11, 20),
                    lines=[
                        OpeningStockLineInput(
                            item_id=self.item_id,
                            quantity=Decimal("10.00"),
                        )
                    ],
                )
            )

    def test_immutable_posted_transactions_and_ledger_entries(self) -> None:
        """Posted transactions and ledger entries cannot be modified or deleted."""
        res = receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("20.00"),
                    )
                ],
            )
        )

        txn = StockTransaction.objects.get(id=res.transaction_id)
        entry = StockLedgerEntry.objects.filter(transaction=txn).first()
        assert entry is not None

        # Cannot modify transaction
        txn.notes = "Tampered notes"
        with pytest.raises(ImmutableStockTransactionError):
            txn.save()

        # Cannot delete transaction
        with pytest.raises(ImmutableStockTransactionError):
            txn.delete()

        # Cannot modify ledger entry
        entry.quantity = Decimal("1000.00")
        with pytest.raises(ImmutableStockTransactionError):
            entry.save()

        # Cannot delete ledger entry
        with pytest.raises(ImmutableStockTransactionError):
            entry.delete()

    def test_ledger_nonzero_quantity_check_constraint(self) -> None:
        """Ledger entry cannot have zero quantity."""
        res = receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("10.00"),
                    )
                ],
            )
        )
        txn = StockTransaction.objects.get(id=res.transaction_id)
        with pytest.raises(IntegrityError):
            StockLedgerEntry.objects.create(
                organization_id=self.org_id,
                transaction=txn,
                item_id=self.item_id,
                warehouse_id=self.warehouse_id,
                quantity=Decimal("0.00"),  # Violates ~Q(quantity=0)
            )

    def test_stock_balance_check_constraints(self) -> None:
        """Negative balance or reserved exceeding on-hand violates DB constraints."""
        # Negative quantity_on_hand
        with transaction.atomic(), pytest.raises(IntegrityError):
            StockBalance.objects.create(
                organization_id=self.org_id,
                warehouse_id=self.warehouse_id,
                item_id=self.item_id,
                quantity_on_hand=Decimal("-5.00"),
                quantity_reserved=Decimal("0.00"),
            )

        # Negative quantity_reserved
        with transaction.atomic(), pytest.raises(IntegrityError):
            StockBalance.objects.create(
                organization_id=self.org_id,
                warehouse_id=self.warehouse_id,
                item_id=self.item_id,
                quantity_on_hand=Decimal("10.00"),
                quantity_reserved=Decimal("-1.00"),
            )

        # Reserved > on hand
        with transaction.atomic(), pytest.raises(IntegrityError):
            StockBalance.objects.create(
                organization_id=self.org_id,
                warehouse_id=self.warehouse_id,
                item_id=self.item_id,
                quantity_on_hand=Decimal("10.00"),
                quantity_reserved=Decimal("15.00"),
            )

    def test_rbac_denial_on_receipt(self) -> None:
        """Member role cannot execute stock receipt commands."""
        with pytest.raises(PermissionDenied):
            receive_opening_stock(
                ReceiveOpeningStockInput(
                    context=self.member_ctx,
                    warehouse_id=self.warehouse_id,
                    transaction_date=date(2026, 11, 20),
                    lines=[
                        OpeningStockLineInput(
                            item_id=self.item_id,
                            quantity=Decimal("10.00"),
                        )
                    ],
                )
            )
