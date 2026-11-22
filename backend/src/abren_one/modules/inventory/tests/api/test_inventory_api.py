import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from abren_one.modules.organizations.public import (
    AddMemberInput,
    CreateOrganizationInput,
    add_member,
    create_organization,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestInventoryAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.owner_user = User.objects.create_user(
            username=f"inv_owner_{uuid.uuid4().hex[:6]}",
            password="secretpassword",
        )
        self.client.force_authenticate(user=self.owner_user)

        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.owner_user.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        self.org_result = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Inventory Test Org",
                slug=f"inv-test-{uuid.uuid4().hex[:6]}",
            )
        )
        self.org_id = self.org_result.organization_id

        owner_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.owner_user.id,
            organization_id=self.org_id,
            correlation_id=uuid.uuid4(),
            actor_role=Role.OWNER.value,
        )

        # Member user with read-only view permissions
        self.member_user = User.objects.create_user(
            username=f"inv_member_{uuid.uuid4().hex[:6]}",
            password="secretpassword",
        )
        add_member(
            AddMemberInput(
                context=owner_ctx,
                user_id=self.member_user.id,
                role=Role.MEMBER.value,
            )
        )

    def test_item_category_api(self) -> None:
        # Create category
        resp = self.client.post(
            "/api/v1/inventory/categories/",
            {
                "name": "Hygiene & Sanitation",
                "code": "WASH",
                "description": "Soap, sanitizers, and water purifiers",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        cat_id = resp.data["category_id"]

        # List categories
        list_resp = self.client.get(
            "/api/v1/inventory/categories/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) >= 1
        assert any(str(c["id"]) == str(cat_id) for c in list_resp.data)

    def test_item_api_lifecycle(self) -> None:
        # Create category first
        cat_resp = self.client.post(
            "/api/v1/inventory/categories/",
            {"name": "Medical Equipment", "code": "MED-EQ"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        cat_id = cat_resp.data["category_id"]

        # Create item
        item_resp = self.client.post(
            "/api/v1/inventory/items/",
            {
                "category_id": cat_id,
                "item_code": "MED-OX-01",
                "name": "Pulse Oximeter",
                "unit_of_measure": "units",
                "item_type": "durable_asset",
                "track_batches": True,
                "reorder_threshold": "10.00",
                "default_unit_cost": "25.00",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert item_resp.status_code == status.HTTP_201_CREATED
        item_id = item_resp.data["item_id"]

        # Add batch
        batch_resp = self.client.post(
            f"/api/v1/inventory/items/{item_id}/batches/",
            {
                "batch_number": "BATCH-OX-001",
                "expiry_date": "2028-12-31",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert batch_resp.status_code == status.HTTP_201_CREATED

        # Get item detail
        detail_resp = self.client.get(
            f"/api/v1/inventory/items/{item_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["name"] == "Pulse Oximeter"
        assert len(detail_resp.data["batches"]) == 1

        # Update item
        update_resp = self.client.put(
            f"/api/v1/inventory/items/{item_id}/",
            {"name": "Pulse Oximeter (Digital LED)", "reorder_threshold": "15.00"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.data["name"] == "Pulse Oximeter (Digital LED)"

    def test_warehouse_api_lifecycle(self) -> None:
        # Create warehouse
        wh_resp = self.client.post(
            "/api/v1/inventory/warehouses/",
            {
                "name": "Dire Dawa Logistics Hub",
                "code": "WH-DIR",
                "warehouse_type": "regional_depot",
                "address": "Dire Dawa Industrial Zone",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert wh_resp.status_code == status.HTTP_201_CREATED
        wh_id = wh_resp.data["warehouse_id"]

        # Add storage location
        loc_resp = self.client.post(
            f"/api/v1/inventory/warehouses/{wh_id}/locations/",
            {"name": "Zone A - Floor", "code": "ZA-FL"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert loc_resp.status_code == status.HTTP_201_CREATED

        # Get warehouse detail
        detail_resp = self.client.get(
            f"/api/v1/inventory/warehouses/{wh_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["code"] == "WH-DIR"
        assert len(detail_resp.data["locations"]) == 1

    def test_rbac_denial(self) -> None:
        """Member role cannot create items or warehouses."""
        member_client = APIClient()
        member_client.force_authenticate(user=self.member_user)

        # Member can view items
        view_resp = member_client.get(
            "/api/v1/inventory/items/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert view_resp.status_code == status.HTTP_200_OK

        # Member cannot create item
        create_resp = member_client.post(
            "/api/v1/inventory/items/",
            {
                "category_id": str(uuid.uuid4()),
                "item_code": "UNAUTH-01",
                "name": "Unauthorized Item",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert create_resp.status_code == status.HTTP_403_FORBIDDEN

        # Member cannot create warehouse
        wh_resp = member_client.post(
            "/api/v1/inventory/warehouses/",
            {"name": "Unauthorized Warehouse", "code": "WH-UNAUTH"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert wh_resp.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_tenant_isolation(self) -> None:
        """Items in Org A cannot be retrieved from Org B context."""
        cat_resp = self.client.post(
            "/api/v1/inventory/categories/",
            {"name": "Emergency Food", "code": "EM-FOOD"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        item_resp = self.client.post(
            "/api/v1/inventory/items/",
            {
                "category_id": cat_resp.data["category_id"],
                "item_code": "RICE-25KG",
                "name": "White Rice 25kg",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        item_id = item_resp.data["item_id"]

        # Create Org B
        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.owner_user.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org_b = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Org B Inventory",
                slug=f"org-b-inv-{uuid.uuid4().hex[:6]}",
            )
        )

        # Accessing Org A item from Org B returns 404
        cross_resp = self.client.get(
            f"/api/v1/inventory/items/{item_id}/",
            HTTP_X_ORGANIZATION_ID=str(org_b.organization_id),
        )
        assert cross_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_stock_intake_and_balances_api(self) -> None:
        """API endpoints for opening stock receipt, donation receipt, and balances."""
        # Setup item and warehouse
        cat_resp = self.client.post(
            "/api/v1/inventory/categories/",
            {"name": "Nutrition", "code": "NUTR"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        item_resp = self.client.post(
            "/api/v1/inventory/items/",
            {
                "category_id": cat_resp.data["category_id"],
                "item_code": "RUTF-01",
                "name": "PlumpyNut RUTF Sachets",
                "unit_of_measure": "cartons",
                "reorder_threshold": "50.00",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        item_id = item_resp.data["item_id"]

        wh_resp = self.client.post(
            "/api/v1/inventory/warehouses/",
            {"name": "Mekelle Depot", "code": "WH-MEK"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        wh_id = wh_resp.data["warehouse_id"]

        # 1. Opening stock receipt
        open_resp = self.client.post(
            "/api/v1/inventory/transactions/receipt-opening/",
            {
                "warehouse_id": wh_id,
                "transaction_date": "2026-11-20",
                "reference_document": "INIT-001",
                "lines": [
                    {
                        "item_id": item_id,
                        "quantity": "200.00",
                        "unit_cost": "45.00",
                    }
                ],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert open_resp.status_code == status.HTTP_201_CREATED
        assert str(open_resp.data["total_quantity"]) == "200.00"

        # 2. Donation receipt
        don_resp = self.client.post(
            "/api/v1/inventory/transactions/receipt-donation/",
            {
                "warehouse_id": wh_id,
                "donor_name": "UNICEF Ethiopia",
                "transaction_date": "2026-11-21",
                "reference_document": "DON-UNI-01",
                "lines": [
                    {
                        "item_id": item_id,
                        "quantity": "50.00",
                        "unit_cost": "45.00",
                    }
                ],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert don_resp.status_code == status.HTTP_201_CREATED
        assert don_resp.data["donor_name"] == "UNICEF Ethiopia"

        # 3. Check stock balances
        bal_resp = self.client.get(
            "/api/v1/inventory/balances/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert bal_resp.status_code == status.HTTP_200_OK
        assert len(bal_resp.data) == 1
        assert bal_resp.data[0]["quantity_on_hand"] == "250.00"

        # 4. Check reconciliation
        rec_resp = self.client.get(
            "/api/v1/inventory/balances/reconciliation/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert rec_resp.status_code == status.HTTP_200_OK
        assert rec_resp.data["is_healthy"] is True
        assert rec_resp.data["discrepancies_count"] == 0

    def test_stock_movements_api(self) -> None:
        """API endpoints for transfer, issue, count adjust, write-off, ledger, and alerts."""
        cat_resp = self.client.post(
            "/api/v1/inventory/categories/",
            {"name": "Water & Sanitation", "code": "WASH-02"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        item_resp = self.client.post(
            "/api/v1/inventory/items/",
            {
                "category_id": cat_resp.data["category_id"],
                "item_code": "PUR-TAB-100",
                "name": "Water Purification Tablets",
                "unit_of_measure": "strips",
                "reorder_threshold": "80.00",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        item_id = item_resp.data["item_id"]

        wh1_resp = self.client.post(
            "/api/v1/inventory/warehouses/",
            {"name": "Depot 1", "code": "WH-DP1"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        wh1_id = wh1_resp.data["warehouse_id"]

        wh2_resp = self.client.post(
            "/api/v1/inventory/warehouses/",
            {"name": "Depot 2", "code": "WH-DP2"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        wh2_id = wh2_resp.data["warehouse_id"]

        # Intake 100 units at WH1
        self.client.post(
            "/api/v1/inventory/transactions/receipt-opening/",
            {
                "warehouse_id": wh1_id,
                "transaction_date": "2026-11-20",
                "lines": [{"item_id": item_id, "quantity": "100.00"}],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )

        # 1. Transfer 30 from WH1 to WH2
        trf_resp = self.client.post(
            "/api/v1/inventory/transactions/transfer/",
            {
                "source_warehouse_id": wh1_id,
                "destination_warehouse_id": wh2_id,
                "transaction_date": "2026-11-21",
                "lines": [{"item_id": item_id, "quantity": "30.00"}],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert trf_resp.status_code == status.HTTP_201_CREATED
        trf_id = trf_resp.data["transaction_id"]

        # 2. Issue 20 from WH1
        iss_resp = self.client.post(
            "/api/v1/inventory/transactions/issue/",
            {
                "warehouse_id": wh1_id,
                "transaction_date": "2026-11-21",
                "lines": [{"item_id": item_id, "quantity": "20.00"}],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert iss_resp.status_code == status.HTTP_201_CREATED

        # 3. Adjust count at WH1 (current is 50, physical is 55)
        adj_resp = self.client.post(
            "/api/v1/inventory/transactions/adjust/",
            {
                "warehouse_id": wh1_id,
                "transaction_date": "2026-11-22",
                "justification": "Physical count audit",
                "lines": [{"item_id": item_id, "actual_quantity_counted": "55.00"}],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert adj_resp.status_code == status.HTTP_201_CREATED
        assert str(adj_resp.data["net_quantity_delta"]) == "5.00"

        # 4. Write off 5 at WH1
        wo_resp = self.client.post(
            "/api/v1/inventory/transactions/write-off/",
            {
                "warehouse_id": wh1_id,
                "transaction_date": "2026-11-22",
                "approval_reference": "WO-AUTH-01",
                "justification": "Packaging damaged during handling",
                "lines": [{"item_id": item_id, "quantity": "5.00", "reason": "damaged"}],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert wo_resp.status_code == status.HTTP_201_CREATED

        # 5. Ledger list
        ledger_resp = self.client.get(
            "/api/v1/inventory/ledger/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert ledger_resp.status_code == status.HTTP_200_OK
        assert len(ledger_resp.data) >= 5

        # 6. Transaction detail
        detail_resp = self.client.get(
            f"/api/v1/inventory/transactions/{trf_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert len(detail_resp.data["entries"]) == 2

        # 7. Stock alerts (reorder threshold is 80, WH1 has 50 -> low stock alert)
        alerts_resp = self.client.get(
            "/api/v1/inventory/alerts/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert alerts_resp.status_code == status.HTTP_200_OK
        assert len(alerts_resp.data["reorder_alerts"]) >= 1
