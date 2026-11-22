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
