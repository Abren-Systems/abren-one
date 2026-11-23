"""Integration tests for Inventory → Finance GL Bridges (ADR-006).

Verifies that inventory operational transactions automatically generate
accurate, balanced, posted double-entry journal entries in the General Ledger
when standard accounts (1200, 2010, 3200, 5000, 5100, 5800) exist, and
gracefully degrade when accounts are not configured.
"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from abren_one.modules.finance.public import (
    AccountType,
    CreateAccountInput,
    JournalEntryStatus,
    create_account,
    get_journal_entry,
    list_journal_entries,
)
from abren_one.modules.inventory.application.commands.create_item import (
    CreateItemInput,
)
from abren_one.modules.inventory.application.commands.create_item import (
    execute as create_item,
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
from abren_one.modules.inventory.application.commands.receive_purchased_stock import (
    ReceivePurchasedStockInput,
    ReceivePurchasedStockLineInput,
)
from abren_one.modules.inventory.application.commands.receive_purchased_stock import (
    execute as receive_purchased_stock,
)
from abren_one.modules.inventory.application.commands.write_off_stock import (
    WriteOffLineInput,
    WriteOffStockInput,
)
from abren_one.modules.inventory.application.commands.write_off_stock import (
    execute as write_off_stock,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.modules.procurement.public import (
    CreatePurchaseOrderInput,
    CreatePurchaseOrderItemInput,
    CreateVendorInput,
    InspectGoodsReceiptInput,
    InspectReceiptItemInput,
    IssuePurchaseOrderInput,
    RecordGoodsReceiptInput,
    RecordReceiptItemInput,
    create_purchase_order,
    create_vendor,
    get_commitment_detail,
    get_grn_details,
    inspect_goods_receipt,
    issue_purchase_order,
    record_goods_receipt,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestInventoryToFinanceGLBridges:
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
                name="Global Relief Network",
                slug=f"grn-{uuid4().hex[:6]}",
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

        # 1. Setup Standard Chart of Accounts (§4.1, ADR-006)
        self.acc_inventory = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="1200",
                name="Inventory Asset",
                account_type=AccountType.ASSET.value,
                currency="USD",
            )
        )
        self.acc_ap_clearing = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="2010",
                name="Accounts Payable - Goods Clearing",
                account_type=AccountType.LIABILITY.value,
                currency="USD",
            )
        )
        self.acc_inkind_revenue = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="3200",
                name="In-Kind Donation Revenue",
                account_type=AccountType.REVENUE.value,
                currency="USD",
            )
        )
        self.acc_general_exp = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="5000",
                name="General Operations Expenditure",
                account_type=AccountType.EXPENSE.value,
                currency="USD",
            )
        )
        self.acc_relief_exp = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="5100",
                name="Program Relief Expenditure",
                account_type=AccountType.EXPENSE.value,
                currency="USD",
            )
        )
        self.acc_shrinkage = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="5800",
                name="Inventory Shrinkage and Loss",
                account_type=AccountType.EXPENSE.value,
                currency="USD",
            )
        )

        # 2. Setup Warehouse & Item Catalog
        self.warehouse = create_warehouse(
            CreateWarehouseInput(
                context=self.admin_ctx,
                code="WH-EAST",
                name="East Warehouse",
                warehouse_type="central",
            )
        )

        cat = create_item_category(
            CreateItemCategoryInput(
                context=self.admin_ctx,
                name="Relief Goods",
                code="RELIEF",
            )
        )
        self.category_id = cat.category_id

        self.item_tarps = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="TARP-SHEET",
                name="Heavy Duty Tarpaulin 4x5m",
                unit_of_measure="piece",
                item_type="relief_good",
                default_unit_cost=Decimal("25.00"),
            )
        )

        self.item_blanket = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="BLANKET-WTR",
                name="Winter Thermal Blanket",
                unit_of_measure="piece",
                item_type="relief_good",
                default_unit_cost=Decimal("15.00"),
            )
        )

    def test_purchase_receipt_automatically_posts_gl_entry(self) -> None:
        """When purchased goods are intaked into inventory, a balanced journal entry
        is automatically posted: Dr 1200 Inventory Asset, Cr 2010 AP Clearing.
        """
        # Create vendor, PO, GRN, inspect
        vendor = create_vendor(
            CreateVendorInput(
                context=self.admin_ctx,
                name="Relief Wholesale Logistics",
                vendor_type="goods",
            )
        )
        po = create_purchase_order(
            CreatePurchaseOrderInput(
                context=self.admin_ctx,
                vendor_id=vendor.vendor_id,
                currency="USD",
                delivery_address="East Logistics Hub",
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Heavy Duty Tarpaulin 4x5m",
                        quantity=Decimal("50.00"),
                        unit="piece",
                        unit_price=Decimal("20.00"),  # Total = $1,000.00
                    ),
                ],
            )
        )
        po_detail = get_commitment_detail(self.org_id, po.order_id)
        po_item = po_detail.items[0]

        issue_purchase_order(
            IssuePurchaseOrderInput(
                context=self.admin_ctx,
                order_id=po.order_id,
            )
        )
        grn_rec = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=self.admin_ctx,
                purchase_order_id=po.order_id,
                received_date=date(2026, 11, 23),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item.po_item_id,
                        quantity_received=Decimal("50.00"),
                    )
                ],
            )
        )
        grn_details = get_grn_details(self.org_id, grn_rec.receipt_id)
        grn_item = grn_details.items[0]

        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=self.admin_ctx,
                receipt_id=grn_rec.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn_item.grn_item_id,
                        quantity_accepted=Decimal("50.00"),
                        quantity_rejected=Decimal("0.00"),
                    )
                ],
            )
        )

        initial_je_count = len(list_journal_entries(self.admin_ctx))

        # Execute inventory intake
        res = receive_purchased_stock(
            ReceivePurchasedStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                goods_receipt_id=grn_rec.receipt_id,
                transaction_date=date(2026, 11, 23),
                lines=[
                    ReceivePurchasedStockLineInput(
                        po_item_id=po_item.po_item_id,
                        item_id=self.item_tarps.item_id,
                        quantity=Decimal("50.00"),
                        unit_cost=Decimal("20.00"),
                    )
                ],
            )
        )

        # Verify a new posted journal entry was generated
        all_jes = list_journal_entries(self.admin_ctx)
        assert len(all_jes) == initial_je_count + 1

        je = next((j for j in all_jes if res.transaction_number in j.memo), None)
        assert je is not None
        assert je.status == JournalEntryStatus.POSTED.value
        assert je.currency == "USD"
        assert "Auto-GL: Purchased stock receipt" in je.memo

        # Fetch lines and verify Dr 1200 ($1000.00) / Cr 2010 ($1000.00)
        je_detail = get_journal_entry(je.id, self.admin_ctx)
        assert je_detail.total_debits == Decimal("1000.00")
        assert je_detail.total_credits == Decimal("1000.00")

        lines_by_code = {line.account_code: line for line in je_detail.lines}
        assert "1200" in lines_by_code
        assert "2010" in lines_by_code

        assert lines_by_code["1200"].debit == Decimal("1000.00")
        assert lines_by_code["1200"].credit == Decimal("0.00")
        assert lines_by_code["2010"].debit == Decimal("0.00")
        assert lines_by_code["2010"].credit == Decimal("1000.00")

    def test_program_stock_issue_automatically_posts_gl_entry(self) -> None:
        """When inventory is issued for program relief delivery, an automatic journal
        entry is posted: Dr 5100 Program Relief Expenditure, Cr 1200 Inventory Asset.
        """
        # First stock up via opening balance
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_tarps.item_id,
                        quantity=Decimal("100.00"),
                        unit_cost=Decimal("25.00"),
                    )
                ],
            )
        )

        initial_jes = len(list_journal_entries(self.admin_ctx))

        # Issue 30 tarps for humanitarian program distribution
        issue_res = issue_stock(
            IssueStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                transaction_date=date(2026, 11, 23),
                is_program_issue=True,
                recipient_name="Flood Relief Beneficiaries Zone A",
                reference_document="DIST-REQ-001",
                lines=[
                    IssueLineInput(
                        item_id=self.item_tarps.item_id,
                        quantity=Decimal("30.00"),
                    )
                ],
            )
        )

        all_jes = list_journal_entries(self.admin_ctx)
        assert len(all_jes) == initial_jes + 1

        je = next((j for j in all_jes if issue_res.transaction_number in j.memo), None)
        assert je is not None
        assert je.status == JournalEntryStatus.POSTED.value
        assert "Auto-GL: Program stock issue" in je.memo

        # 30 units * default unit cost ($25.00) = $750.00
        je_detail = get_journal_entry(je.id, self.admin_ctx)
        assert je_detail.total_debits == Decimal("750.00")
        assert je_detail.total_credits == Decimal("750.00")

        lines_by_code = {line.account_code: line for line in je_detail.lines}
        assert lines_by_code["5100"].debit == Decimal("750.00")
        assert lines_by_code["1200"].credit == Decimal("750.00")

    def test_general_stock_issue_automatically_posts_gl_entry(self) -> None:
        """When inventory is issued for general operations (internal use), Dr 5000 / Cr 1200."""
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_blanket.item_id,
                        quantity=Decimal("40.00"),
                        unit_cost=Decimal("15.00"),
                    )
                ],
            )
        )

        issue_res = issue_stock(
            IssueStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                transaction_date=date(2026, 11, 23),
                is_program_issue=False,
                recipient_name="Field Staff Office",
                lines=[
                    IssueLineInput(
                        item_id=self.item_blanket.item_id,
                        quantity=Decimal("10.00"),
                    )
                ],
            )
        )

        je = next((j for j in list_journal_entries(self.admin_ctx) if issue_res.transaction_number in j.memo), None)
        assert je is not None
        je_detail = get_journal_entry(je.id, self.admin_ctx)
        assert je_detail.total_debits == Decimal("150.00")
        lines_by_code = {line.account_code: line for line in je_detail.lines}
        assert lines_by_code["5000"].debit == Decimal("150.00")
        assert lines_by_code["1200"].credit == Decimal("150.00")

    def test_write_off_disposal_automatically_posts_gl_entry(self) -> None:
        """When stock is written off due to damage or expiry, Dr 5800 / Cr 1200."""
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_tarps.item_id,
                        quantity=Decimal("20.00"),
                        unit_cost=Decimal("25.00"),
                    )
                ],
            )
        )

        wo_res = write_off_stock(
            WriteOffStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                transaction_date=date(2026, 11, 23),
                approval_reference="EXEC-DISP-2026-08",
                justification="Water damage during warehouse roof leak",
                lines=[
                    WriteOffLineInput(
                        item_id=self.item_tarps.item_id,
                        quantity=Decimal("5.00"),
                        reason="Water damaged",
                    )
                ],
            )
        )

        je = next((j for j in list_journal_entries(self.admin_ctx) if wo_res.transaction_number in j.memo), None)
        assert je is not None
        # 5 units * $25.00 = $125.00
        je_detail = get_journal_entry(je.id, self.admin_ctx)
        assert je_detail.total_debits == Decimal("125.00")
        lines_by_code = {line.account_code: line for line in je_detail.lines}
        assert lines_by_code["5800"].debit == Decimal("125.00")
        assert lines_by_code["1200"].credit == Decimal("125.00")

    def test_in_kind_donation_automatically_posts_gl_entry(self) -> None:
        """When an in-kind stock donation is received, Dr 1200 / Cr 3200."""
        don_res = receive_in_kind_donation(
            ReceiveDonationInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse.warehouse_id,
                donor_name="Red Crescent Humanitarian Aid",
                transaction_date=date(2026, 11, 23),
                reference_document="DON-GIFT-449",
                lines=[
                    DonationReceiptLineInput(
                        item_id=self.item_blanket.item_id,
                        quantity=Decimal("100.00"),
                        unit_cost=Decimal("12.00"),  # Fair market valuation: $1,200.00
                    )
                ],
            )
        )

        je = next((j for j in list_journal_entries(self.admin_ctx) if don_res.transaction_number in j.memo), None)
        assert je is not None
        je_detail = get_journal_entry(je.id, self.admin_ctx)
        assert je_detail.total_debits == Decimal("1200.00")
        lines_by_code = {line.account_code: line for line in je_detail.lines}
        assert lines_by_code["1200"].debit == Decimal("1200.00")
        assert lines_by_code["3200"].credit == Decimal("1200.00")

    def test_graceful_degradation_when_accounts_not_configured(self) -> None:
        """When an organization hasn't set up standard GL accounts, inventory
        transactions succeed cleanly without errors or partial failures.
        """
        # Create a second organization with NO accounts created
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid4(),
        )
        new_org = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Grassroots Community Aid",
                slug=f"gca-{uuid4().hex[:6]}",
            )
        )
        gca_ctx = ExecutionContext(
            organization_id=new_org.organization_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )

        wh = create_warehouse(
            CreateWarehouseInput(
                context=gca_ctx,
                code="WH-LOCAL",
                name="Local Storage",
                warehouse_type="regional_depot",
            )
        )
        cat = create_item_category(
            CreateItemCategoryInput(
                context=gca_ctx,
                name="Local Food",
                code="FOOD",
            )
        )
        item = create_item(
            CreateItemInput(
                context=gca_ctx,
                category_id=cat.category_id,
                item_code="RICE-25KG",
                name="Rice Bag 25kg",
                unit_of_measure="bag",
                item_type="relief_good",
            )
        )

        # In-kind donation succeeds without GL accounts
        don_res = receive_in_kind_donation(
            ReceiveDonationInput(
                context=gca_ctx,
                warehouse_id=wh.warehouse_id,
                donor_name="Local Merchant",
                transaction_date=date(2026, 11, 23),
                lines=[
                    DonationReceiptLineInput(
                        item_id=item.item_id,
                        quantity=Decimal("20.00"),
                        unit_cost=Decimal("15.00"),
                    )
                ],
            )
        )
        assert don_res.total_quantity == Decimal("20.00")

        # No journal entry created, but inventory operation succeeded
        assert len(list_journal_entries(gca_ctx)) == 0
