"""End-to-End Humanitarian Operational Loop Integration Test (ADR-006).

Demonstrates the complete, integrated operational lifecycle of a humanitarian NGO:
1. Organization initialization & Chart of Accounts setup
2. Fundraising: Donor grant & monetary donation intake → Auto-GL Cash / Revenue
3. Procurement: PO issuance, physical delivery, and quality inspection
4. Inventory Intake: Goods receipt into warehouse → Auto-GL Inventory Asset / AP Clearing
5. Beneficiaries: Aid distribution of physical relief goods → Stock Issue & Auto-GL Program Expense
6. Inventory Management: Authorized write-off of damaged stock → Auto-GL Shrinkage Loss
7. Finance: Complete General Ledger and Trial Balance reconciliation (Debits == Credits)
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from abren_one.modules.beneficiaries.public import (
    BeneficiaryType,
    RecordServiceDeliveryInput,
    RegisterBeneficiaryInput,
    ServiceType,
    VulnerabilityLevel,
    record_service_delivery,
    register_beneficiary,
)
from abren_one.modules.finance.public import (
    AccountType,
    CreateAccountInput,
    create_account,
    get_journal_entry,
    get_trial_balance,
    list_journal_entries,
)
from abren_one.modules.fundraising.public import (
    ActivateGrantInput,
    AwardGrantInput,
    CreateDonorInput,
    CreateGrantInput,
    DonorType,
    PaymentMethod,
    RecordDonationInput,
    activate_grant,
    award_grant,
    create_donor,
    create_grant,
    record_donation,
)
from abren_one.modules.inventory.public import (
    CreateItemCategoryInput,
    CreateItemInput,
    CreateWarehouseInput,
    ReceivePurchasedStockInput,
    ReceivePurchasedStockLineInput,
    WriteOffLineInput,
    WriteOffStockInput,
    create_item,
    create_item_category,
    create_warehouse,
    get_stock_balances,
    receive_purchased_stock,
    write_off_stock,
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
from abren_one.modules.programs.public import (
    CreateProgramInput,
    create_program,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestHumanitarianOperationalLoop:
    def test_full_operational_loop_and_gl_reconciliation(self) -> None:
        # ── 1. Organization & Security Context ─────────────────────────
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid4(),
        )
        org_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="International Disaster Relief Agency",
                slug=f"idra-{uuid4().hex[:6]}",
            )
        )
        org_id = org_res.organization_id

        admin_ctx = ExecutionContext(
            organization_id=org_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )

        # ── 2. Chart of Accounts Setup (§4.1, ADR-006) ─────────────────
        create_account(
            CreateAccountInput(
                context=admin_ctx,
                code="1010",
                name="Cash and Operating Bank",
                account_type=AccountType.ASSET.value,
                currency="USD",
            )
        )
        create_account(
            CreateAccountInput(
                context=admin_ctx,
                code="1200",
                name="Inventory Asset",
                account_type=AccountType.ASSET.value,
                currency="USD",
            )
        )
        create_account(
            CreateAccountInput(
                context=admin_ctx,
                code="2010",
                name="Accounts Payable - Goods Clearing",
                account_type=AccountType.LIABILITY.value,
                currency="USD",
            )
        )
        create_account(
            CreateAccountInput(
                context=admin_ctx,
                code="3100",
                name="Temporarily Restricted Grant Revenue",
                account_type=AccountType.REVENUE.value,
                currency="USD",
            )
        )
        create_account(
            CreateAccountInput(
                context=admin_ctx,
                code="5100",
                name="Program Relief Expenditure",
                account_type=AccountType.EXPENSE.value,
                currency="USD",
            )
        )
        create_account(
            CreateAccountInput(
                context=admin_ctx,
                code="5800",
                name="Inventory Shrinkage and Spoilage",
                account_type=AccountType.EXPENSE.value,
                currency="USD",
            )
        )

        # ── 3. Program Setup ───────────────────────────────────────────
        prog_res = create_program(
            CreateProgramInput(
                context=admin_ctx,
                name="Emergency Earthquake Response 2026",
                description="Relief food, shelter, and medical assistance",
            )
        )
        program_id = prog_res.program_id

        # ── 4. Fundraising: Donor, Grant & Donation Intake ─────────────
        donor = create_donor(
            CreateDonorInput(
                context=admin_ctx,
                name="UN Humanitarian Pooled Fund",
                donor_type=DonorType.FOUNDATION.value,
                email="grants@unhpf.org",
            )
        )
        grant = create_grant(
            CreateGrantInput(
                context=admin_ctx,
                donor_id=donor.donor_id,
                title="Rapid Earthquake Response Grant",
                reference_code="UN-EQ-2026-001",
                total_amount=Decimal("100000.00"),
                currency="USD",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
                program_id=program_id,
            )
        )
        award_grant(AwardGrantInput(context=admin_ctx, grant_id=grant.grant_id))
        activate_grant(ActivateGrantInput(context=admin_ctx, grant_id=grant.grant_id))

        # Receive first tranche: $100,000.00
        donation_res = record_donation(
            RecordDonationInput(
                context=admin_ctx,
                donor_id=donor.donor_id,
                grant_id=grant.grant_id,
                program_id=program_id,
                amount=Decimal("100000.00"),
                currency="USD",
                payment_method=PaymentMethod.BANK_TRANSFER.value,
                reference="UN-WIRE-98214",
                received_at=datetime(2026, 11, 23, 8, 30, tzinfo=UTC),
            )
        )
        assert donation_res.donation_id is not None

        # Verify Auto-GL for Donation: Dr 1010 ($100k) / Cr 3100 ($100k)
        jes_step1 = list_journal_entries(admin_ctx)
        assert len(jes_step1) == 1
        je1_detail = get_journal_entry(jes_step1[0].id, admin_ctx)
        assert je1_detail.total_debits == Decimal("100000.00")
        assert je1_detail.grant_id == grant.grant_id

        # ── 5. Procurement: Vendor, Purchase Order & Goods Receipt ─────
        vendor = create_vendor(
            CreateVendorInput(
                context=admin_ctx,
                name="Global Food Aid Logistics FZCO",
                vendor_type="goods",
            )
        )
        po = create_purchase_order(
            CreatePurchaseOrderInput(
                context=admin_ctx,
                vendor_id=vendor.vendor_id,
                currency="USD",
                delivery_address="Aleppo Central Warehouse",
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Emergency Family Food Parcel 20kg",
                        quantity=Decimal("200.00"),
                        unit="parcel",
                        unit_price=Decimal("25.00"),  # 200 * $25 = $5,000.00
                    )
                ],
            )
        )
        po_detail = get_commitment_detail(org_id, po.order_id)
        po_item = po_detail.items[0]

        issue_purchase_order(
            IssuePurchaseOrderInput(
                context=admin_ctx,
                order_id=po.order_id,
            )
        )

        grn = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=admin_ctx,
                purchase_order_id=po.order_id,
                received_date=date(2026, 11, 23),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item.po_item_id,
                        quantity_received=Decimal("200.00"),
                    )
                ],
            )
        )
        grn_details = get_grn_details(org_id, grn.receipt_id)
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=admin_ctx,
                receipt_id=grn.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn_details.items[0].grn_item_id,
                        quantity_accepted=Decimal("200.00"),
                        quantity_rejected=Decimal("0.00"),
                    )
                ],
            )
        )

        # ── 6. Inventory Intake: Stock Ledger & GL Asset/AP Posting ────
        wh = create_warehouse(
            CreateWarehouseInput(
                context=admin_ctx,
                code="WH-CENTRAL",
                name="Aleppo Central Warehouse",
                warehouse_type="central",
            )
        )
        cat = create_item_category(
            CreateItemCategoryInput(
                context=admin_ctx,
                name="Food Assistance",
                code="FOOD",
            )
        )
        item_food = create_item(
            CreateItemInput(
                context=admin_ctx,
                category_id=cat.category_id,
                item_code="FOOD-PARCEL-20KG",
                name="Emergency Family Food Parcel 20kg",
                unit_of_measure="parcel",
                item_type="relief_good",
                default_unit_cost=Decimal("25.00"),
            )
        )

        intake_res = receive_purchased_stock(
            ReceivePurchasedStockInput(
                context=admin_ctx,
                warehouse_id=wh.warehouse_id,
                goods_receipt_id=grn.receipt_id,
                transaction_date=date(2026, 11, 23),
                lines=[
                    ReceivePurchasedStockLineInput(
                        po_item_id=po_item.po_item_id,
                        item_id=item_food.item_id,
                        quantity=Decimal("200.00"),
                        unit_cost=Decimal("25.00"),
                    )
                ],
            )
        )
        assert intake_res.total_quantity == Decimal("200.00")

        # Verify Auto-GL for Inventory Intake: Dr 1200 ($5,000) / Cr 2010 ($5,000)
        jes_step2 = list_journal_entries(admin_ctx)
        assert len(jes_step2) == 2
        je2 = next(j for j in jes_step2 if intake_res.transaction_number in j.memo)
        je2_detail = get_journal_entry(je2.id, admin_ctx)
        assert je2_detail.total_debits == Decimal("5000.00")
        assert je2_detail.total_credits == Decimal("5000.00")

        # ── 7. Beneficiaries: Aid Delivery & Stock Issue Bridge ────────
        ben = register_beneficiary(
            RegisterBeneficiaryInput(
                context=admin_ctx,
                beneficiary_type=BeneficiaryType.HOUSEHOLD.value,
                household_name="Kabbani Displaced Family",
                vulnerability_level=VulnerabilityLevel.HIGH.value,
            )
        )

        # Distribute 50 food parcels to the refugee camp (Value = 50 * $25 = $1,250.00)
        deliv_res = record_service_delivery(
            RecordServiceDeliveryInput(
                context=admin_ctx,
                beneficiary_id=ben.beneficiary_id,
                service_type=ServiceType.FOOD_ASSISTANCE.value,
                delivery_date=date(2026, 11, 23),
                quantity=Decimal("50.00"),
                unit="parcel",
                program_id=program_id,
                warehouse_id=wh.warehouse_id,
                item_id=item_food.item_id,
                notes="First distribution cycle at Camp Bravo",
            )
        )
        assert deliv_res.inventory_transaction_id is not None

        # Verify Auto-GL for Program Stock Issue: Dr 5100 ($1,250) / Cr 1200 ($1,250)
        jes_step3 = list_journal_entries(admin_ctx)
        assert len(jes_step3) == 3
        je3 = next(j for j in jes_step3 if deliv_res.inventory_transaction_number in j.memo)
        je3_detail = get_journal_entry(je3.id, admin_ctx)
        assert je3_detail.total_debits == Decimal("1250.00")

        # ── 8. Inventory Write-off: Damaged Stock Disposal ─────────────
        # 2 parcels damaged by rain during transit (Value = 2 * $25 = $50.00)
        wo_res = write_off_stock(
            WriteOffStockInput(
                context=admin_ctx,
                warehouse_id=wh.warehouse_id,
                transaction_date=date(2026, 11, 23),
                approval_reference="DISP-LOG-2026-004",
                justification="Rain water seepage on loading dock",
                lines=[
                    WriteOffLineInput(
                        item_id=item_food.item_id,
                        quantity=Decimal("2.00"),
                        reason="Water damaged",
                    )
                ],
            )
        )

        # Verify Auto-GL for Write-off: Dr 5800 ($50) / Cr 1200 ($50)
        jes_step4 = list_journal_entries(admin_ctx)
        assert len(jes_step4) == 4
        je4 = next(j for j in jes_step4 if wo_res.transaction_number in j.memo)
        je4_detail = get_journal_entry(je4.id, admin_ctx)
        assert je4_detail.total_debits == Decimal("50.00")

        # ── 9. Final Inventory Stock Balance Verification ──────────────
        # 200 intaked - 50 distributed - 2 written off = 148 remaining
        final_balances = get_stock_balances(
            admin_ctx,
            warehouse_id=wh.warehouse_id,
            item_id=item_food.item_id,
        )
        assert len(final_balances) == 1
        assert final_balances[0].quantity_on_hand == Decimal("148.00")

        # ── 10. Final General Ledger & Trial Balance Reconciliation ────
        trial_balance = get_trial_balance(admin_ctx)

        # Total debits must equal total credits exactly
        assert trial_balance.is_balanced is True
        assert trial_balance.total_debits == Decimal("105000.00")
        assert trial_balance.total_credits == Decimal("105000.00")

        tb_by_code = {item.code: item for item in trial_balance.items}

        # 1010 Operating Bank (Asset): $100,000.00 Dr
        assert tb_by_code["1010"].balance_debit == Decimal("100000.00")
        assert tb_by_code["1010"].balance_credit == Decimal("0.00")

        # 1200 Inventory Asset (Asset): $5,000 Dr - $1,250 Cr - $50 Cr = $3,700.00 Net Dr
        # (148 units on hand * $25.00 default unit cost = $3,700.00 exact match!)
        assert tb_by_code["1200"].total_debit == Decimal("5000.00")
        assert tb_by_code["1200"].total_credit == Decimal("1300.00")
        assert tb_by_code["1200"].balance_debit == Decimal("3700.00")
        assert tb_by_code["1200"].balance_credit == Decimal("0.00")

        # 2010 Accounts Payable Clearing (Liability): $5,000.00 Cr
        assert tb_by_code["2010"].balance_credit == Decimal("5000.00")

        # 3100 Restricted Grant Revenue (Revenue): $100,000.00 Cr
        assert tb_by_code["3100"].balance_credit == Decimal("100000.00")

        # 5100 Program Relief Expenditure (Expense): $1,250.00 Dr
        assert tb_by_code["5100"].balance_debit == Decimal("1250.00")

        # 5800 Inventory Shrinkage and Spoilage (Expense): $50.00 Dr
        assert tb_by_code["5800"].balance_debit == Decimal("50.00")
