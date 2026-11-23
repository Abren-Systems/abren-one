"""End-to-End Humanitarian Supply Chain Integration Test.

Exercises the complete cross-module operating lifecycle across all participating domains
through public module APIs only:

1. Provision Organization, Branch, and Department (organizations.public)
2. Create strategic Program, Project, and operational Activity (programs.public)
3. Award Grant, register Donor, and record funding tranche (fundraising.public)
4. Setup Chart of Accounts and post funding journal entry (finance.public)
5. Purchase Requisition, Approval, Purchase Order, and Delivery GRN (procurement.public)
6. Finance Commitment & Delivery Reconciliation (procurement.public)
7. Stock Intake from GRN into Central Warehouse with batch tracking (inventory.public)
8. Inter-warehouse transfer to Regional Field Depot (inventory.public)
9. Stock Issue to Program Beneficiary Distribution Activity (inventory.public)
10. End-to-end ledger reconciliation and cross-domain audit trail verification.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from abren_one.modules.finance.public import (
    AccountType,
    CreateAccountInput,
    CreateJournalEntryInput,
    JournalLineInput,
    PostJournalEntryInput,
    create_account,
    create_journal_entry,
    get_trial_balance,
    post_journal_entry,
)
from abren_one.modules.fundraising.public import (
    ActivateGrantInput,
    AwardGrantInput,
    CreateDonorInput,
    CreateGrantInput,
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
    IssueLineInput,
    IssueStockInput,
    ReceivePurchasedStockInput,
    ReceivePurchasedStockLineInput,
    TransferLineInput,
    TransferStockInput,
    create_item,
    create_item_category,
    create_warehouse,
    get_stock_balances,
    get_stock_ledger,
    issue_stock,
    list_pending_grns,
    receive_purchased_stock,
    reconcile_balances,
    transfer_stock,
)
from abren_one.modules.organizations.public import (
    AddMemberInput,
    CreateBranchInput,
    CreateDepartmentInput,
    CreateOrganizationInput,
    add_member,
    create_branch,
    create_department,
    create_organization,
)
from abren_one.modules.procurement.public import (
    ApprovePurchaseRequisitionInput,
    CreatePurchaseOrderInput,
    CreatePurchaseOrderItemInput,
    CreatePurchaseRequisitionInput,
    CreateRequisitionItemInput,
    CreateVendorInput,
    InspectGoodsReceiptInput,
    InspectReceiptItemInput,
    IssuePurchaseOrderInput,
    RecordGoodsReceiptInput,
    RecordReceiptItemInput,
    SubmitPurchaseRequisitionInput,
    approve_purchase_requisition,
    create_purchase_order,
    create_purchase_requisition,
    create_vendor,
    get_accepted_receipts_for_order,
    get_commitment_detail,
    get_grn_details,
    get_outstanding_commitments,
    inspect_goods_receipt,
    issue_purchase_order,
    record_goods_receipt,
    submit_purchase_requisition,
)
from abren_one.modules.programs.public import (
    CreateActivityInput,
    CreateProgramInput,
    CreateProjectInput,
    create_activity,
    create_program,
    create_project,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestSupplyChainLifecycleWorkflow:
    """Verifies that an NGO can run its full supply-chain lifecycle across all modules."""

    def test_full_supply_chain_pipeline(self) -> None:
        user_model = get_user_model()
        user_director = user_model.objects.create_user(
            username=f"director_{uuid.uuid4().hex[:8]}",
            password="testpassword123",
        )
        user_approver = user_model.objects.create_user(
            username=f"approver_{uuid.uuid4().hex[:8]}",
            password="testpassword123",
        )

        correlation_id = uuid.uuid4()

        # ===================================================================
        # 1. Provision Organization, Branch, and Department
        # ===================================================================
        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user_director.id,
            organization_id=None,
            correlation_id=correlation_id,
        )

        org_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="International Humanitarian Relief",
                slug=f"ihr-{uuid.uuid4().hex[:6]}",
            )
        )
        org_id = org_res.organization_id

        # Staff Contexts
        director_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user_director.id,
            organization_id=org_id,
            actor_role=Role.OWNER.value,
            correlation_id=correlation_id,
        )

        approver_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user_approver.id,
            organization_id=org_id,
            actor_role=Role.ADMIN.value,
            correlation_id=correlation_id,
        )
        add_member(
            AddMemberInput(
                context=director_ctx,
                user_id=user_approver.id,
                role=Role.ADMIN.value,
            )
        )

        branch_res = create_branch(
            CreateBranchInput(
                context=director_ctx,
                name="Horn of Africa Regional Office",
                code="HOA-01",
            )
        )
        branch_id = branch_res.branch_id

        dept_res = create_department(
            CreateDepartmentInput(
                context=director_ctx,
                name="Logistics and Supply Chain",
                code="LOG-OPS",
            )
        )
        dept_id = dept_res.department_id

        # ===================================================================
        # 2. Strategic Program, Project, and Operational Activity
        # ===================================================================
        prog_res = create_program(
            CreateProgramInput(
                context=director_ctx,
                name="Emergency Shelter and NFI Response",
                description="Rapid non-food items and shelter assistance for displaced populations.",
            )
        )
        program_id = prog_res.program_id

        proj_res = create_project(
            CreateProjectInput(
                context=director_ctx,
                program_id=program_id,
                name="Flood Response 2026",
            )
        )
        project_id = proj_res.project_id

        act_res = create_activity(
            CreateActivityInput(
                context=director_ctx,
                project_id=project_id,
                name="Rapid Winterization Kit Distribution",
            )
        )
        activity_id = act_res.activity_id

        # ===================================================================
        # 3. Institutional Donor, Grant, and Funding Tranche
        # ===================================================================
        donor_res = create_donor(
            CreateDonorInput(
                context=director_ctx,
                name="UN OCHA Emergency Response Fund",
                donor_type="institutional",
                email="erf@un.org",
            )
        )
        donor_id = donor_res.donor_id

        grant_res = create_grant(
            CreateGrantInput(
                context=director_ctx,
                donor_id=donor_id,
                title="Horn of Africa Flood & Shelter Relief Grant",
                reference_code=f"GRN-{uuid.uuid4().hex[:6].upper()}",
                total_amount=Decimal("100000.00"),
                currency="USD",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
                program_id=program_id,
            )
        )
        grant_id = grant_res.grant_id
        assert grant_id is not None

        # Award and activate the grant to transition from PROPOSED -> AWARDED -> ACTIVE
        award_res = award_grant(
            AwardGrantInput(
                context=director_ctx,
                grant_id=grant_id,
                notes="Grant awarded by OCHA panel",
            )
        )
        assert award_res.status == "awarded"

        activate_res = activate_grant(
            ActivateGrantInput(
                context=director_ctx,
                grant_id=grant_id,
                notes="Grant agreement countersigned and effective",
            )
        )
        assert activate_res.status == "active"

        record_donation(
            RecordDonationInput(
                context=director_ctx,
                donor_id=donor_id,
                amount=Decimal("50000.00"),
                currency="USD",
                received_at=timezone.now(),
                grant_id=grant_id,
                program_id=program_id,
                reference="TR-OCHA-2026-001",
            )
        )

        # ===================================================================
        # 4. Chart of Accounts & Finance Funding Journal
        # ===================================================================
        acc_bank = create_account(
            CreateAccountInput(
                context=director_ctx,
                code="1010",
                name="Main Operational Bank Account",
                account_type=AccountType.ASSET.value,
                currency="USD",
            )
        ).account_id

        acc_rev = create_account(
            CreateAccountInput(
                context=director_ctx,
                code="4010",
                name="Institutional Grant Revenue",
                account_type=AccountType.REVENUE.value,
                currency="USD",
            )
        ).account_id

        # Post grant funding journal entry
        je_res = create_journal_entry(
            CreateJournalEntryInput(
                context=director_ctx,
                entry_date=date(2026, 1, 15),
                memo="Tranche 1 Grant Disbursement Received",
                currency="USD",
                lines=[
                    JournalLineInput(
                        account_id=acc_bank,
                        debit=Decimal("50000.00"),
                        credit=Decimal("0.00"),
                        memo="Bank receipt",
                    ),
                    JournalLineInput(
                        account_id=acc_rev,
                        debit=Decimal("0.00"),
                        credit=Decimal("50000.00"),
                        memo="Recognize grant revenue",
                    ),
                ],
            )
        )
        post_journal_entry(
            PostJournalEntryInput(
                context=director_ctx,
                journal_entry_id=je_res.journal_entry_id,
            )
        )

        # Verify balanced trial balance
        tb = get_trial_balance(director_ctx)
        assert tb.is_balanced is True
        assert tb.total_debits == Decimal("50000.00")
        assert tb.total_credits == Decimal("50000.00")

        # ===================================================================
        # 5. Procurement: Requisition, PO, Delivery, and Inspection
        # ===================================================================
        vendor_res = create_vendor(
            CreateVendorInput(
                context=director_ctx,
                name="Global Shelter & Relief Direct",
                vendor_type="goods",
                default_payment_terms="Net 30",
            )
        )
        vendor_id = vendor_res.vendor_id

        # Requisition created by Director
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=director_ctx,
                title="Emergency Tarpaulins & Thermal Blankets",
                currency="USD",
                items=[
                    CreateRequisitionItemInput(
                        description="Heavy-Duty Tarpaulins 4x5m",
                        quantity=Decimal("500.00"),
                        unit="piece",
                        estimated_unit_price=Decimal("20.00"),
                        program_id=program_id,
                        activity_id=activity_id,
                        department_id=dept_id,
                    ),
                    CreateRequisitionItemInput(
                        description="Thermal Winter Blankets",
                        quantity=Decimal("300.00"),
                        unit="blanket",
                        estimated_unit_price=Decimal("15.00"),
                        program_id=program_id,
                        activity_id=activity_id,
                        department_id=dept_id,
                    ),
                ],
            )
        )
        req_id = req_res.requisition_id

        # Submit requisition
        submit_purchase_requisition(
            SubmitPurchaseRequisitionInput(
                context=director_ctx,
                requisition_id=req_id,
            )
        )

        # Approve requisition by designated Approver (segregation of duties)
        approve_purchase_requisition(
            ApprovePurchaseRequisitionInput(
                context=approver_ctx,
                requisition_id=req_id,
            )
        )

        # Create Purchase Order against requisition
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=director_ctx,
                vendor_id=vendor_id,
                requisition_id=req_id,
                currency="USD",
                delivery_address="Central Logistics Hub, Nairobi",
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Heavy-Duty Tarpaulins 4x5m",
                        quantity=Decimal("500.00"),
                        unit="piece",
                        unit_price=Decimal("20.00"),
                    ),
                    CreatePurchaseOrderItemInput(
                        description="Thermal Winter Blankets",
                        quantity=Decimal("300.00"),
                        unit="blanket",
                        unit_price=Decimal("15.00"),
                    ),
                ],
            )
        )
        po_id = po_res.order_id

        # Issue PO
        issue_purchase_order(
            IssuePurchaseOrderInput(
                context=director_ctx,
                order_id=po_id,
            )
        )

        # Verify Finance Commitment tracking
        commitments = get_outstanding_commitments(org_id)
        assert len(commitments) >= 1
        po_commitment = next(c for c in commitments if c.po_id == po_id)
        assert po_commitment.total_committed == Decimal("14500.00")
        assert po_commitment.total_outstanding == Decimal("14500.00")

        # Get PO line item IDs
        po_detail = get_commitment_detail(org_id, po_id)
        tarp_po_item = next(i for i in po_detail.items if "Tarpaulins" in i.description)
        blkt_po_item = next(i for i in po_detail.items if "Blankets" in i.description)

        # Delivery Arrival: Record Goods Receipt Note (GRN)
        grn_res = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=director_ctx,
                purchase_order_id=po_id,
                received_date=date(2026, 2, 1),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=tarp_po_item.po_item_id,
                        quantity_received=Decimal("500.00"),
                    ),
                    RecordReceiptItemInput(
                        po_item_id=blkt_po_item.po_item_id,
                        quantity_received=Decimal("300.00"),
                    ),
                ],
            )
        )
        grn_id = grn_res.receipt_id

        # Inspect GRN: 480 Tarpaulins accepted, 20 rejected; 300 Blankets accepted
        grn_details = get_grn_details(org_id, grn_id)
        tarp_grn_item = next(i for i in grn_details.items if i.po_item_id == tarp_po_item.po_item_id)
        blkt_grn_item = next(i for i in grn_details.items if i.po_item_id == blkt_po_item.po_item_id)

        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=director_ctx,
                receipt_id=grn_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=tarp_grn_item.grn_item_id,
                        quantity_accepted=Decimal("480.00"),
                        quantity_rejected=Decimal("20.00"),
                        rejection_reason="Torn edge seam",
                    ),
                    InspectReceiptItemInput(
                        grn_item_id=blkt_grn_item.grn_item_id,
                        quantity_accepted=Decimal("300.00"),
                        quantity_rejected=Decimal("0.00"),
                    ),
                ],
            )
        )

        # Verify accepted receipts in Procurement
        accepted_receipts = get_accepted_receipts_for_order(org_id, po_id)
        total_accepted_val = sum((r.accepted_value for r in accepted_receipts), Decimal("0.00"))
        # 480 * 20 + 300 * 15 = 9600 + 4500 = 14100
        assert total_accepted_val == Decimal("14100.00")

        # ===================================================================
        # 6. Inventory Intake: Warehouses, Items & GRN Intake
        # ===================================================================
        wh_central = create_warehouse(
            CreateWarehouseInput(
                context=director_ctx,
                code="WH-CENTRAL",
                name="Nairobi Central Logistics Hub",
                warehouse_type="central",
                branch_id=branch_id,
            )
        ).warehouse_id

        wh_field = create_warehouse(
            CreateWarehouseInput(
                context=director_ctx,
                code="WH-FIELD",
                name="Garissa Field Distribution Depot",
                warehouse_type="regional_depot",
                branch_id=branch_id,
            )
        ).warehouse_id

        cat_shelter = create_item_category(
            CreateItemCategoryInput(
                context=director_ctx,
                name="Emergency Shelter Items",
                code="CAT-SHELTER",
            )
        ).category_id

        item_tarp = create_item(
            CreateItemInput(
                context=director_ctx,
                category_id=cat_shelter,
                item_code="TARP-HD-4X5",
                name="Heavy-Duty Tarpaulins 4x5m",
                unit_of_measure="piece",
                item_type="relief_good",
            )
        ).item_id

        item_blkt = create_item(
            CreateItemInput(
                context=director_ctx,
                category_id=cat_shelter,
                item_code="BLKT-THERMAL",
                name="Thermal Winter Blankets",
                unit_of_measure="blanket",
                item_type="relief_good",
                track_batches=True,
                track_expiry=True,
            )
        ).item_id

        # Verify pending GRN exists in inventory query
        pending = list_pending_grns(director_ctx)
        assert any(p.grn_id == grn_id for p in pending)

        # Receive accepted stock into Central Warehouse
        intake_res = receive_purchased_stock(
            ReceivePurchasedStockInput(
                context=director_ctx,
                warehouse_id=wh_central,
                goods_receipt_id=grn_id,
                transaction_date=date(2026, 2, 2),
                lines=[
                    ReceivePurchasedStockLineInput(
                        po_item_id=tarp_po_item.po_item_id,
                        item_id=item_tarp,
                        quantity=Decimal("480.00"),
                    ),
                    ReceivePurchasedStockLineInput(
                        po_item_id=blkt_po_item.po_item_id,
                        item_id=item_blkt,
                        quantity=Decimal("300.00"),
                        batch_number="LOT-2026-BLKT01",
                        expiry_date=date(2029, 12, 31),
                    ),
                ],
                notes="Intake verified against physical delivery",
            )
        )
        assert intake_res.total_quantity == Decimal("780.00")

        # Verify stock balances at Central Warehouse
        bal_c_tarp = get_stock_balances(director_ctx, warehouse_id=wh_central, item_id=item_tarp)
        assert bal_c_tarp[0].quantity_on_hand == Decimal("480.00")

        bal_c_blkt = get_stock_balances(director_ctx, warehouse_id=wh_central, item_id=item_blkt)
        assert bal_c_blkt[0].quantity_on_hand == Decimal("300.00")
        assert bal_c_blkt[0].batch_number == "LOT-2026-BLKT01"

        # ===================================================================
        # 7. Inter-Warehouse Stock Transfer (Central -> Field Depot)
        # ===================================================================
        transfer_res = transfer_stock(
            TransferStockInput(
                context=director_ctx,
                source_warehouse_id=wh_central,
                destination_warehouse_id=wh_field,
                transaction_date=date(2026, 2, 5),
                lines=[
                    TransferLineInput(
                        item_id=item_tarp,
                        quantity=Decimal("200.00"),
                    ),
                    TransferLineInput(
                        item_id=item_blkt,
                        quantity=Decimal("150.00"),
                        batch_id=bal_c_blkt[0].batch_id,
                    ),
                ],
                reference_document="WAYBILL-2026-001",
                notes="Convoy dispatch to Garissa Field Hub",
            )
        )
        assert transfer_res.total_lines == 2
        assert transfer_res.total_quantity_transferred == Decimal("350.00")

        # Verify stock balance split after transfer
        # Central: 480 - 200 = 280 tarpaulins; 300 - 150 = 150 blankets
        assert get_stock_balances(director_ctx, warehouse_id=wh_central, item_id=item_tarp)[
            0
        ].quantity_on_hand == Decimal("280.00")
        assert get_stock_balances(director_ctx, warehouse_id=wh_central, item_id=item_blkt)[
            0
        ].quantity_on_hand == Decimal("150.00")

        # Field: 200 tarpaulins; 150 blankets
        assert get_stock_balances(director_ctx, warehouse_id=wh_field, item_id=item_tarp)[
            0
        ].quantity_on_hand == Decimal("200.00")
        assert get_stock_balances(director_ctx, warehouse_id=wh_field, item_id=item_blkt)[
            0
        ].quantity_on_hand == Decimal("150.00")

        # ===================================================================
        # 8. Field Stock Issue to Program Beneficiary Activity
        # ===================================================================
        bal_f_blkt = get_stock_balances(director_ctx, warehouse_id=wh_field, item_id=item_blkt)

        issue_res = issue_stock(
            IssueStockInput(
                context=director_ctx,
                warehouse_id=wh_field,
                transaction_date=date(2026, 2, 10),
                is_program_issue=True,
                recipient_name="Garissa Community Elders Relief Committee",
                reference_document="DIST-LOG-2026-01",
                notes="Distributed to 120 flood-affected households",
                lines=[
                    IssueLineInput(
                        item_id=item_tarp,
                        quantity=Decimal("120.00"),
                        program_id=program_id,
                        activity_id=activity_id,
                    ),
                    IssueLineInput(
                        item_id=item_blkt,
                        quantity=Decimal("100.00"),
                        batch_id=bal_f_blkt[0].batch_id,
                        program_id=program_id,
                        activity_id=activity_id,
                    ),
                ],
            )
        )
        assert issue_res.total_lines == 2
        assert issue_res.total_quantity_issued == Decimal("220.00")
        assert issue_res.transaction_type == "issue_program"

        # Verify remaining Field balances
        # Field: 200 - 120 = 80 tarpaulins; 150 - 100 = 50 blankets
        assert get_stock_balances(director_ctx, warehouse_id=wh_field, item_id=item_tarp)[
            0
        ].quantity_on_hand == Decimal("80.00")
        assert get_stock_balances(director_ctx, warehouse_id=wh_field, item_id=item_blkt)[
            0
        ].quantity_on_hand == Decimal("50.00")

        # Check ledger attribution for issues
        ledger = get_stock_ledger(director_ctx, warehouse_id=wh_field, item_id=item_tarp)
        issue_entry = next(e for e in ledger if e.quantity == Decimal("-120.00"))
        assert issue_entry.program_id == program_id
        assert issue_entry.activity_id == activity_id

        # ===================================================================
        # 9. Audit Trail & Ledger Integrity Across Domains
        # ===================================================================
        # Verify 100% healthy reconciliation (materialized balances == sum of ledger)
        reconcile_report = reconcile_balances(director_ctx)
        assert reconcile_report.is_healthy is True
        assert reconcile_report.discrepancies_count == 0

        # Verify Audit Trail captures cross-domain actions
        org_audit_events = AuditEvent.objects.filter(organization_id=org_id)
        assert org_audit_events.exists()

        action_names = set(org_audit_events.values_list("action", flat=True))
        # Organizations
        assert "organization.created" in action_names
        assert "branch.created" in action_names
        assert "department.created" in action_names
        # Programs
        assert "program.created" in action_names
        assert "project.created" in action_names
        assert "activity.created" in action_names
        # Fundraising
        assert "fundraising.donor.created" in action_names
        assert "fundraising.grant.created" in action_names
        assert "fundraising.grant.awarded" in action_names
        assert "fundraising.grant.activated" in action_names
        assert "fundraising.donation.recorded" in action_names
        # Finance
        assert "finance.account.created" in action_names
        assert "finance.journal_entry.posted" in action_names
        # Procurement
        assert "procurement.requisition.approved" in action_names
        assert "procurement.order.issued" in action_names
        assert "procurement.receipt.recorded" in action_names
        assert "procurement.receipt.inspected" in action_names
        # Inventory
        assert "inventory.warehouse.created" in action_names
        assert "inventory.item.created" in action_names
        assert "inventory.stock.purchase_received" in action_names
        assert "inventory.stock.transferred" in action_names
        assert "inventory.stock.issued" in action_names
