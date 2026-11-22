from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied

from abren_one.modules.inventory.application.commands.adjust_stock import (
    AdjustmentLineInput,
    AdjustStockInput,
)
from abren_one.modules.inventory.application.commands.adjust_stock import (
    execute as adjust_stock,
)
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
from abren_one.modules.inventory.application.commands.issue_stock import (
    IssueLineInput,
    IssueStockInput,
)
from abren_one.modules.inventory.application.commands.issue_stock import (
    execute as issue_stock,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    OpeningStockLineInput,
    ReceiveOpeningStockInput,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    execute as receive_opening_stock,
)
from abren_one.modules.inventory.application.commands.transfer_stock import (
    TransferLineInput,
    TransferStockInput,
)
from abren_one.modules.inventory.application.commands.transfer_stock import (
    execute as transfer_stock,
)
from abren_one.modules.inventory.application.commands.write_off_stock import (
    WriteOffLineInput,
    WriteOffStockInput,
)
from abren_one.modules.inventory.application.commands.write_off_stock import (
    execute as write_off_stock,
)
from abren_one.modules.inventory.application.queries.get_expiring_batches import (
    execute as get_expiring_batches,
)
from abren_one.modules.inventory.application.queries.get_reorder_alerts import (
    execute as get_reorder_alerts,
)
from abren_one.modules.inventory.application.queries.get_stock_balances import (
    execute as get_stock_balances,
)
from abren_one.modules.inventory.application.queries.get_stock_ledger import (
    execute as get_stock_ledger,
)
from abren_one.modules.inventory.application.queries.reconcile_balances import (
    execute as reconcile_balances,
)
from abren_one.modules.inventory.domain.exceptions import (
    ExpiredStockIssueError,
    InsufficientStockError,
    InventoryError,
    SameWarehouseTransferError,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestPhase3OperationalMovements:
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
                name="Health Relief Ops",
                slug=f"health-relief-{uuid4().hex[:6]}",
            )
        )
        self.org_id = org_res.organization_id

        self.admin_ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )
        self.staff_ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.STAFF.value,
            correlation_id=uuid4(),
        )
        self.member_ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.MEMBER.value,
            correlation_id=uuid4(),
        )

        cat_res = create_item_category(
            CreateItemCategoryInput(context=self.admin_ctx, name="Pharmaceuticals", code="PHARM")
        )
        self.category_id = cat_res.category_id

        # Standard item with reorder threshold
        item_res = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="PHARM-PAR-500",
                name="Paracetamol 500mg Tablets",
                unit_of_measure="strips",
                reorder_threshold=Decimal("100.00"),
                default_unit_cost=Decimal("1.20"),
            )
        )
        self.item_id = item_res.item_id

        # Batch-tracked item
        batch_item_res = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="PHARM-INS-100",
                name="Insulin Glargine Vials",
                unit_of_measure="vials",
                track_batches=True,
                track_expiry=True,
                reorder_threshold=Decimal("20.00"),
            )
        )
        self.batch_item_id = batch_item_res.item_id

        # 2 Warehouses
        wh_a = create_warehouse(
            CreateWarehouseInput(
                context=self.admin_ctx,
                name="Addis Central Hub",
                code="WH-ADD",
            )
        )
        self.wh_a_id = wh_a.warehouse_id

        wh_b = create_warehouse(
            CreateWarehouseInput(
                context=self.admin_ctx,
                name="Hawassa Field Post",
                code="WH-HAW",
            )
        )
        self.wh_b_id = wh_b.warehouse_id

        # Receive opening stock of 100 paracetamol at WH-A
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("100.00"),
                    )
                ],
            )
        )

    def test_inter_warehouse_transfer_conservation_of_mass(self) -> None:
        """Transfer 40 units from WH-A to WH-B: sum of deltas is 0, balances update."""
        res = transfer_stock(
            TransferStockInput(
                context=self.staff_ctx,
                source_warehouse_id=self.wh_a_id,
                destination_warehouse_id=self.wh_b_id,
                transaction_date=date(2026, 11, 22),
                reference_document="TRF-ADD-HAW-001",
                notes="Replenishing Hawassa stock",
                lines=[
                    TransferLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("40.00"),
                    )
                ],
            )
        )

        assert res.total_quantity_transferred == Decimal("40.00")

        # Verify balances
        bal_a = get_stock_balances(self.admin_ctx, warehouse_id=self.wh_a_id, item_id=self.item_id)[0]
        bal_b = get_stock_balances(self.admin_ctx, warehouse_id=self.wh_b_id, item_id=self.item_id)[0]

        assert bal_a.quantity_on_hand == Decimal("60.00")
        assert bal_b.quantity_on_hand == Decimal("40.00")

        # Verify ledger entries sum to 0
        ledger = get_stock_ledger(self.admin_ctx, transaction_id=res.transaction_id)
        assert len(ledger) == 2
        total_delta = sum(e.quantity for e in ledger)
        assert total_delta == Decimal("0.00")

        # Balance reconciliation passes
        rec = reconcile_balances(self.admin_ctx)
        assert rec.is_healthy

    def test_transfer_same_warehouse_fails(self) -> None:
        """Transferring to the same warehouse raises SameWarehouseTransferError."""
        with pytest.raises(SameWarehouseTransferError):
            transfer_stock(
                TransferStockInput(
                    context=self.staff_ctx,
                    source_warehouse_id=self.wh_a_id,
                    destination_warehouse_id=self.wh_a_id,
                    transaction_date=date(2026, 11, 22),
                    lines=[
                        TransferLineInput(
                            item_id=self.item_id,
                            quantity=Decimal("10.00"),
                        )
                    ],
                )
            )

    def test_transfer_overselling_fails(self) -> None:
        """Attempting to transfer more than available stock raises InsufficientStockError."""
        with pytest.raises(InsufficientStockError):
            transfer_stock(
                TransferStockInput(
                    context=self.staff_ctx,
                    source_warehouse_id=self.wh_a_id,
                    destination_warehouse_id=self.wh_b_id,
                    transaction_date=date(2026, 11, 22),
                    lines=[
                        TransferLineInput(
                            item_id=self.item_id,
                            quantity=Decimal("150.00"),  # Only 100 available!
                        )
                    ],
                )
            )

    def test_general_and_program_stock_issue(self) -> None:
        """General and program issues reduce stock balance and record operational context."""
        prog_id = uuid4()
        act_id = uuid4()

        # General issue
        res_gen = issue_stock(
            IssueStockInput(
                context=self.staff_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date(2026, 11, 22),
                is_program_issue=False,
                recipient_name="Staff First Aid Depot",
                lines=[
                    IssueLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("15.00"),
                    )
                ],
            )
        )
        assert res_gen.total_quantity_issued == Decimal("15.00")

        # Program issue
        res_prog = issue_stock(
            IssueStockInput(
                context=self.staff_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date(2026, 11, 22),
                is_program_issue=True,
                recipient_name="Hawassa Community Clinic",
                lines=[
                    IssueLineInput(
                        item_id=self.item_id,
                        quantity=Decimal("35.00"),
                        program_id=prog_id,
                        activity_id=act_id,
                    )
                ],
            )
        )
        assert res_prog.total_quantity_issued == Decimal("35.00")

        # Balance at WH-A: 100 - 15 - 35 = 50
        bal = get_stock_balances(self.admin_ctx, warehouse_id=self.wh_a_id, item_id=self.item_id)[0]
        assert bal.quantity_on_hand == Decimal("50.00")

        # Reorder threshold check: threshold is 100, on hand is 50 -> low stock alert!
        assert bal.is_low_stock
        alerts = get_reorder_alerts(self.admin_ctx, warehouse_id=self.wh_a_id)
        assert len(alerts) == 1
        assert alerts[0].shortage_quantity == Decimal("50.00")

    def test_expired_batch_blocked_from_issue_allowed_for_write_off(self) -> None:
        """Expired batch cannot be issued to programs, but can be disposed via write-off."""
        past_date = date.today() - timedelta(days=10)
        batch_res = create_item_batch(
            CreateItemBatchInput(
                context=self.admin_ctx,
                item_id=self.batch_item_id,
                batch_number="LOT-EXP-001",
                expiry_date=past_date,
            )
        )
        expired_batch_id = batch_res.batch_id

        # Receive opening stock of expired batch
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date(2026, 11, 1),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.batch_item_id,
                        quantity=Decimal("25.00"),
                        batch_id=expired_batch_id,
                    )
                ],
            )
        )

        # Query expiring batches: should report already expired
        exp_alerts = get_expiring_batches(self.admin_ctx, warehouse_id=self.wh_a_id)
        assert len(exp_alerts) >= 1
        exp_item = next(a for a in exp_alerts if a.batch_id == expired_batch_id)
        assert exp_item.is_already_expired

        # Attempting to issue expired batch must be rejected
        with pytest.raises(ExpiredStockIssueError):
            issue_stock(
                IssueStockInput(
                    context=self.staff_ctx,
                    warehouse_id=self.wh_a_id,
                    transaction_date=date.today(),
                    lines=[
                        IssueLineInput(
                            item_id=self.batch_item_id,
                            quantity=Decimal("5.00"),
                            batch_id=expired_batch_id,
                        )
                    ],
                )
            )

        # Writing off the expired batch must succeed
        write_off_res = write_off_stock(
            WriteOffStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date.today(),
                approval_reference="QA-DISP-2026-004",
                justification="Certified batch expired, authorized biomedical destruction",
                lines=[
                    WriteOffLineInput(
                        item_id=self.batch_item_id,
                        quantity=Decimal("25.00"),
                        reason="expired",
                        batch_id=expired_batch_id,
                    )
                ],
            )
        )
        assert write_off_res.total_quantity_written_off == Decimal("25.00")

        # Balance is now 0
        bal = get_stock_balances(
            self.admin_ctx,
            warehouse_id=self.wh_a_id,
            item_id=self.batch_item_id,
        )[0]
        assert bal.quantity_on_hand == Decimal("0.00")

    def test_cycle_count_adjustment(self) -> None:
        """Physical cycle count reconciles discrepancies with positive or negative deltas."""
        # Current balance is 100. Physical count shows 105 (+5 surplus)
        adj_res1 = adjust_stock(
            AdjustStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date(2026, 11, 22),
                justification="Physical count month-end audit",
                lines=[
                    AdjustmentLineInput(
                        item_id=self.item_id,
                        actual_quantity_counted=Decimal("105.00"),
                    )
                ],
            )
        )
        assert adj_res1.net_quantity_delta == Decimal("5.00")

        bal1 = get_stock_balances(self.admin_ctx, warehouse_id=self.wh_a_id, item_id=self.item_id)[0]
        assert bal1.quantity_on_hand == Decimal("105.00")

        # Next count shows 98 (-7 shrinkage)
        adj_res2 = adjust_stock(
            AdjustStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date(2026, 11, 22),
                justification="Re-count after packaging verification",
                lines=[
                    AdjustmentLineInput(
                        item_id=self.item_id,
                        actual_quantity_counted=Decimal("98.00"),
                    )
                ],
            )
        )
        assert adj_res2.net_quantity_delta == Decimal("-7.00")

        bal2 = get_stock_balances(self.admin_ctx, warehouse_id=self.wh_a_id, item_id=self.item_id)[0]
        assert bal2.quantity_on_hand == Decimal("98.00")

        # Zero delta raises error
        with pytest.raises(InventoryError):
            adjust_stock(
                AdjustStockInput(
                    context=self.admin_ctx,
                    warehouse_id=self.wh_a_id,
                    transaction_date=date(2026, 11, 22),
                    justification="Count with no discrepancy",
                    lines=[
                        AdjustmentLineInput(
                            item_id=self.item_id,
                            actual_quantity_counted=Decimal("98.00"),
                        )
                    ],
                )
            )

    def test_rbac_segregation_of_duties(self) -> None:
        """Staff can transfer and issue, but cannot adjust counts or write-off stock."""
        # Staff can transfer
        transfer_stock(
            TransferStockInput(
                context=self.staff_ctx,
                source_warehouse_id=self.wh_a_id,
                destination_warehouse_id=self.wh_b_id,
                transaction_date=date(2026, 11, 22),
                lines=[TransferLineInput(item_id=self.item_id, quantity=Decimal("5.00"))],
            )
        )

        # Staff can issue
        issue_stock(
            IssueStockInput(
                context=self.staff_ctx,
                warehouse_id=self.wh_a_id,
                transaction_date=date(2026, 11, 22),
                lines=[IssueLineInput(item_id=self.item_id, quantity=Decimal("5.00"))],
            )
        )

        # Staff CANNOT adjust count (Owner/Admin only)
        with pytest.raises(PermissionDenied):
            adjust_stock(
                AdjustStockInput(
                    context=self.staff_ctx,
                    warehouse_id=self.wh_a_id,
                    transaction_date=date(2026, 11, 22),
                    justification="Staff attempting count adjustment",
                    lines=[AdjustmentLineInput(item_id=self.item_id, actual_quantity_counted=Decimal("90.00"))],
                )
            )

        # Staff CANNOT write off stock (Owner/Admin only)
        with pytest.raises(PermissionDenied):
            write_off_stock(
                WriteOffStockInput(
                    context=self.staff_ctx,
                    warehouse_id=self.wh_a_id,
                    transaction_date=date(2026, 11, 22),
                    approval_reference="UNAUTH",
                    justification="Staff attempting disposal",
                    lines=[WriteOffLineInput(item_id=self.item_id, quantity=Decimal("2.00"), reason="damaged")],
                )
            )

        # Member CANNOT issue
        with pytest.raises(PermissionDenied):
            issue_stock(
                IssueStockInput(
                    context=self.member_ctx,
                    warehouse_id=self.wh_a_id,
                    transaction_date=date(2026, 11, 22),
                    lines=[IssueLineInput(item_id=self.item_id, quantity=Decimal("1.00"))],
                )
            )
