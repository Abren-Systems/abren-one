"""Integration tests for Procurement GRN intake into Inventory stock balances."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from rest_framework import status
from rest_framework.test import APIClient

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
from abren_one.modules.inventory.application.commands.receive_purchased_stock import (
    ReceivePurchasedStockInput,
    ReceivePurchasedStockLineInput,
)
from abren_one.modules.inventory.application.commands.receive_purchased_stock import (
    execute as receive_purchased_stock,
)
from abren_one.modules.inventory.application.queries.get_stock_balances import (
    execute as get_stock_balances,
)
from abren_one.modules.inventory.application.queries.get_stock_ledger import (
    execute as get_stock_ledger,
)
from abren_one.modules.inventory.application.queries.list_pending_grns import (
    execute as list_pending_grns,
)
from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.domain.value_objects import TransactionType
from abren_one.modules.inventory.models import StockTransaction
from abren_one.modules.organizations.public import (
    AddMemberInput,
    CreateOrganizationInput,
    add_member,
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
    inspect_goods_receipt,
    issue_purchase_order,
    record_goods_receipt,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestProcurementToInventoryIntake:
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
                name="Disaster Relief Services",
                slug=f"drs-{uuid4().hex[:6]}",
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

        # 1. Setup Inventory Catalog & Warehouse
        cat_res = create_item_category(
            CreateItemCategoryInput(
                context=self.admin_ctx,
                name="Shelter Supplies",
                code="SHELTER",
            )
        )
        self.category_id = cat_res.category_id

        self.item_tarpaulin = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="TARP-4X5",
                name="Tarpaulins Heavy Duty 4x5m",
                unit_of_measure="piece",
                item_type="relief_good",
            )
        )

        self.item_hygiene = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="HYG-FAMILY",
                name="Family Hygiene Kit",
                unit_of_measure="kit",
                item_type="relief_good",
            )
        )

        self.item_medical = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="MED-ANTIBIOTIC",
                name="Amoxicillin 500mg",
                unit_of_measure="box",
                item_type="consumable",
                track_batches=True,
                track_expiry=True,
            )
        )

        self.wh_central = create_warehouse(
            CreateWarehouseInput(
                context=self.admin_ctx,
                code="WH-CENTRAL",
                name="Central Logistics Hub",
                warehouse_type="central",
            )
        )

        # 2. Setup Procurement: Vendor, PO, GRN
        vendor = create_vendor(
            CreateVendorInput(
                context=self.admin_ctx,
                name="Relief Supplies Direct Ltd",
                vendor_type="goods",
                default_payment_terms="Net 30",
            )
        )
        self.vendor_id = vendor.vendor_id

        po = create_purchase_order(
            CreatePurchaseOrderInput(
                context=self.admin_ctx,
                vendor_id=self.vendor_id,
                currency="USD",
                delivery_address="Central Logistics Hub",
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Tarpaulins Heavy Duty 4x5m",
                        quantity=Decimal("100.00"),
                        unit="piece",
                        unit_price=Decimal("15.00"),
                    ),
                    CreatePurchaseOrderItemInput(
                        description="Family Hygiene Kit",
                        quantity=Decimal("50.00"),
                        unit="kit",
                        unit_price=Decimal("25.00"),
                    ),
                ],
            )
        )
        self.po_id = po.order_id

        from abren_one.modules.procurement.public import (
            get_commitment_detail,
            get_grn_details,
        )

        po_detail = get_commitment_detail(self.org_id, self.po_id)
        self.po_items = po_detail.items
        self.tarp_po = next(p for p in self.po_items if "Tarpaulins" in p.description)
        self.hyg_po = next(p for p in self.po_items if "Hygiene" in p.description)

        # Issue PO
        issue_purchase_order(
            IssuePurchaseOrderInput(
                context=self.admin_ctx,
                order_id=self.po_id,
            )
        )

        # Record GRN
        grn_rec = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=self.admin_ctx,
                purchase_order_id=self.po_id,
                received_date=date(2026, 11, 20),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=self.tarp_po.po_item_id,
                        quantity_received=Decimal("100.00"),
                    ),
                    RecordReceiptItemInput(
                        po_item_id=self.hyg_po.po_item_id,
                        quantity_received=Decimal("50.00"),
                    ),
                ],
            )
        )
        self.grn_id = grn_rec.receipt_id

        # Inspect GRN: 90 tarpaulins accepted, 10 rejected; 50 hygiene kits accepted
        grn_details = get_grn_details(self.org_id, self.grn_id)
        self.grn_items = grn_details.items
        self.tarp_grn = next(g for g in self.grn_items if g.po_item_id == self.tarp_po.po_item_id)
        self.hyg_grn = next(g for g in self.grn_items if g.po_item_id == self.hyg_po.po_item_id)

        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=self.admin_ctx,
                receipt_id=self.grn_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=self.tarp_grn.grn_item_id,
                        quantity_accepted=Decimal("90.00"),
                        quantity_rejected=Decimal("10.00"),
                        rejection_reason="Torn grommets",
                    ),
                    InspectReceiptItemInput(
                        grn_item_id=self.hyg_grn.grn_item_id,
                        quantity_accepted=Decimal("50.00"),
                        quantity_rejected=Decimal("0.00"),
                    ),
                ],
            )
        )

    def test_list_pending_grns_for_intake(self) -> None:
        """Verified that inspected GRNs with accepted items appear in pending intake query."""
        pending = list_pending_grns(self.admin_ctx)
        assert len(pending) >= 1
        target_grn = next((g for g in pending if g.grn_id == self.grn_id), None)
        assert target_grn is not None
        assert target_grn.total_items == 2
        tarps = next(item for item in target_grn.items if item.po_item_id == self.tarp_po.po_item_id)
        assert tarps.quantity_accepted == Decimal("90.00")
        assert tarps.quantity_remaining == Decimal("90.00")

    def test_receive_purchased_stock_partial_and_complete(self) -> None:
        """Receive partial stock, verify balance and remaining quantity, then receive remaining."""
        # Step 1: Receive partial 40 tarpaulins
        res1 = receive_purchased_stock(
            ReceivePurchasedStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_central.warehouse_id,
                goods_receipt_id=self.grn_id,
                transaction_date=date(2026, 11, 21),
                lines=[
                    ReceivePurchasedStockLineInput(
                        po_item_id=self.tarp_po.po_item_id,
                        item_id=self.item_tarpaulin.item_id,
                        quantity=Decimal("40.00"),
                    )
                ],
                notes="First truckload from supplier",
            )
        )

        assert res1.total_quantity == Decimal("40.00")
        assert res1.goods_receipt_id == self.grn_id
        assert res1.purchase_order_id == self.po_id

        # Verify transaction document
        txn = StockTransaction.objects.get(id=res1.transaction_id)
        assert txn.transaction_type == TransactionType.RECEIPT_PURCHASE.value
        assert txn.goods_receipt_id == self.grn_id
        assert txn.purchase_order_id == self.po_id

        # Verify balance projection
        balances = get_stock_balances(
            self.admin_ctx,
            warehouse_id=self.wh_central.warehouse_id,
            item_id=self.item_tarpaulin.item_id,
        )
        assert len(balances) == 1
        assert balances[0].quantity_on_hand == Decimal("40.00")
        assert balances[0].available_quantity == Decimal("40.00")

        # Verify pending list shows remaining 50 tarpaulins
        pending_after = list_pending_grns(self.admin_ctx)
        target = next(g for g in pending_after if g.grn_id == self.grn_id)
        tarp_line = next(i for i in target.items if i.po_item_id == self.tarp_po.po_item_id)
        assert tarp_line.quantity_already_received == Decimal("40.00")
        assert tarp_line.quantity_remaining == Decimal("50.00")

        # Step 2: Receive remaining 50 tarpaulins and all 50 hygiene kits
        res2 = receive_purchased_stock(
            ReceivePurchasedStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_central.warehouse_id,
                goods_receipt_id=self.grn_id,
                transaction_date=date(2026, 11, 22),
                lines=[
                    ReceivePurchasedStockLineInput(
                        po_item_id=self.tarp_po.po_item_id,
                        item_id=self.item_tarpaulin.item_id,
                        quantity=Decimal("50.00"),
                    ),
                    ReceivePurchasedStockLineInput(
                        po_item_id=self.hyg_po.po_item_id,
                        item_id=self.item_hygiene.item_id,
                        quantity=Decimal("50.00"),
                    ),
                ],
                notes="Second truckload finalizing delivery",
            )
        )
        assert res2.total_quantity == Decimal("100.00")

        # Verify final balances
        bal_tarp = get_stock_balances(
            self.admin_ctx,
            warehouse_id=self.wh_central.warehouse_id,
            item_id=self.item_tarpaulin.item_id,
        )
        assert bal_tarp[0].quantity_on_hand == Decimal("90.00")

        bal_hyg = get_stock_balances(
            self.admin_ctx,
            warehouse_id=self.wh_central.warehouse_id,
            item_id=self.item_hygiene.item_id,
        )
        assert bal_hyg[0].quantity_on_hand == Decimal("50.00")

        # Verify pending list has no remaining items for this GRN
        pending_done = list_pending_grns(self.admin_ctx)
        assert not any(g.grn_id == self.grn_id for g in pending_done)

    def test_over_intake_rejected(self) -> None:
        """Attempting to receive more than accepted quantity must fail."""
        with pytest.raises(InventoryError, match="exceeds remaining accepted quantity"):
            receive_purchased_stock(
                ReceivePurchasedStockInput(
                    context=self.admin_ctx,
                    warehouse_id=self.wh_central.warehouse_id,
                    goods_receipt_id=self.grn_id,
                    transaction_date=date(2026, 11, 21),
                    lines=[
                        ReceivePurchasedStockLineInput(
                            po_item_id=self.tarp_po.po_item_id,
                            item_id=self.item_tarpaulin.item_id,
                            quantity=Decimal("95.00"),  # Only 90 accepted!
                        )
                    ],
                )
            )

    def test_batch_tracked_purchase_intake(self) -> None:
        """Batch-tracked items enforce lot/batch assignment on receipt."""
        # Attempting without batch must raise InventoryError
        with pytest.raises(InventoryError, match="Batch identification is required"):
            receive_purchased_stock(
                ReceivePurchasedStockInput(
                    context=self.admin_ctx,
                    warehouse_id=self.wh_central.warehouse_id,
                    goods_receipt_id=self.grn_id,
                    transaction_date=date(2026, 11, 21),
                    lines=[
                        ReceivePurchasedStockLineInput(
                            po_item_id=self.hyg_po.po_item_id,
                            item_id=self.item_medical.item_id,
                            quantity=Decimal("10.00"),
                        )
                    ],
                )
            )

        # Providing batch_number succeeds and auto-creates batch
        res = receive_purchased_stock(
            ReceivePurchasedStockInput(
                context=self.admin_ctx,
                warehouse_id=self.wh_central.warehouse_id,
                goods_receipt_id=self.grn_id,
                transaction_date=date(2026, 11, 21),
                lines=[
                    ReceivePurchasedStockLineInput(
                        po_item_id=self.hyg_po.po_item_id,
                        item_id=self.item_medical.item_id,
                        quantity=Decimal("10.00"),
                        batch_number="LOT-2026-MED01",
                        expiry_date=date(2027, 12, 31),
                    )
                ],
            )
        )
        assert res.total_quantity == Decimal("10.00")

        ledger = get_stock_ledger(self.admin_ctx, item_id=self.item_medical.item_id)
        assert len(ledger) == 1
        assert ledger[0].batch_number == "LOT-2026-MED01"

    def test_cross_organization_isolation(self) -> None:
        """Organization B cannot access or receive stock from Organization A's GRN."""
        org_b = create_organization(
            CreateOrganizationInput(
                context=ExecutionContext(
                    actor_type=ActorType.SYSTEM,
                    actor_id=None,
                    organization_id=None,
                    correlation_id=uuid4(),
                ),
                name="Another NGO",
                slug=f"another-ngo-{uuid4().hex[:6]}",
            )
        )
        admin_b = ExecutionContext(
            organization_id=org_b.organization_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )
        wh_b = create_warehouse(
            CreateWarehouseInput(
                context=admin_b,
                code="WH-B",
                name="Branch Warehouse",
                warehouse_type="regional_depot",
            )
        )

        with pytest.raises(InventoryError, match="not found or inaccessible"):
            receive_purchased_stock(
                ReceivePurchasedStockInput(
                    context=admin_b,
                    warehouse_id=wh_b.warehouse_id,
                    goods_receipt_id=self.grn_id,  # From Org A!
                    transaction_date=date(2026, 11, 21),
                    lines=[
                        ReceivePurchasedStockLineInput(
                            po_item_id=self.tarp_po.po_item_id,
                            item_id=self.item_tarpaulin.item_id,
                            quantity=Decimal("10.00"),
                        )
                    ],
                )
            )

    def test_receive_purchase_api_endpoint(self) -> None:
        """Test REST API endpoint POST /api/v1/inventory/transactions/receive-purchase/."""
        from django.contrib.auth import get_user_model

        user_cls = get_user_model()
        user = user_cls.objects.create_user(
            username=f"admin_{uuid4().hex[:8]}",
            email=f"admin_{uuid4().hex[:8]}@example.com",
            password="testpassword",
        )
        add_member(
            AddMemberInput(
                context=self.admin_ctx,
                user_id=user.id,
                role=Role.ADMIN.value,
            )
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # GET pending GRNs
        get_res = client.get(
            "/api/v1/inventory/pending-grns/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert get_res.status_code == status.HTTP_200_OK
        assert len(get_res.data) >= 1

        # POST intake
        post_payload = {
            "warehouse_id": str(self.wh_central.warehouse_id),
            "goods_receipt_id": str(self.grn_id),
            "transaction_date": "2026-11-21",
            "reference_document": "GRN-DELIVERY-01",
            "notes": "Received via API test",
            "lines": [
                {
                    "po_item_id": str(self.tarp_po.po_item_id),
                    "item_id": str(self.item_tarpaulin.item_id),
                    "quantity": "25.00",
                }
            ],
        }

        post_res = client.post(
            "/api/v1/inventory/transactions/receive-purchase/",
            data=post_payload,
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert post_res.status_code == status.HTTP_201_CREATED
        assert post_res.data["total_quantity"] == "25.00"
        assert post_res.data["goods_receipt_id"] == str(self.grn_id)
