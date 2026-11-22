import uuid
from datetime import date

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
class TestProcurementAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.owner_user = User.objects.create_user(
            username=f"owner_{uuid.uuid4().hex[:6]}",
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
                name="Horn Relief Procurement",
                slug=f"horn-proc-{uuid.uuid4().hex[:6]}",
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

        # Secondary user in the same org
        self.staff_user = User.objects.create_user(
            username=f"staff_{uuid.uuid4().hex[:6]}",
            password="secretpassword",
        )
        add_member(
            AddMemberInput(
                context=owner_ctx,
                user_id=self.staff_user.id,
                role=Role.STAFF.value,
            )
        )

        # Member user with minimal read permissions
        self.member_user = User.objects.create_user(
            username=f"member_{uuid.uuid4().hex[:6]}",
            password="secretpassword",
        )
        add_member(
            AddMemberInput(
                context=owner_ctx,
                user_id=self.member_user.id,
                role=Role.MEMBER.value,
            )
        )

    def test_vendor_api_lifecycle(self) -> None:
        # Create vendor
        create_resp = self.client.post(
            "/api/v1/procurement/vendors/",
            {
                "name": "Global Medical Supplies",
                "vendor_type": "goods",
                "tax_id": "TAX-9988",
                "default_currency": "USD",
                "default_payment_terms": "Net 30",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        vendor_id = create_resp.data["vendor_id"]

        # List vendors
        list_resp = self.client.get(
            "/api/v1/procurement/vendors/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["name"] == "Global Medical Supplies"

        # Get vendor detail
        detail_resp = self.client.get(
            f"/api/v1/procurement/vendors/{vendor_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["default_payment_terms"] == "Net 30"

        # Update vendor
        update_resp = self.client.put(
            f"/api/v1/procurement/vendors/{vendor_id}/",
            {"default_payment_terms": "Net 60"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert update_resp.status_code == status.HTTP_200_OK

        # Deactivate vendor
        deact_resp = self.client.post(
            f"/api/v1/procurement/vendors/{vendor_id}/deactivate/",
            {"reason": "Contract ended"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert deact_resp.status_code == status.HTTP_200_OK
        assert deact_resp.data["is_active"] is False

    def test_full_procurement_workflow_via_api(self) -> None:
        # 1. Create vendor
        v_resp = self.client.post(
            "/api/v1/procurement/vendors/",
            {"name": "School Books Publishing", "default_payment_terms": "Net 30"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        vendor_id = v_resp.data["vendor_id"]

        # 2. Staff user creates Purchase Requisition
        staff_client = APIClient()
        staff_client.force_authenticate(user=self.staff_user)

        pr_resp = staff_client.post(
            "/api/v1/procurement/requisitions/",
            {
                "title": "Textbooks for Grade 4",
                "items": [
                    {
                        "description": "Math Textbooks",
                        "quantity": "50.00",
                        "unit": "books",
                        "estimated_unit_price": "10.00",
                    }
                ],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert pr_resp.status_code == status.HTTP_201_CREATED
        req_id = pr_resp.data["requisition_id"]

        # 3. Staff submits requisition
        sub_resp = staff_client.post(
            f"/api/v1/procurement/requisitions/{req_id}/submit/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert sub_resp.status_code == status.HTTP_200_OK
        assert sub_resp.data["authorization_status"] == "submitted"

        # 4. Owner approves requisition
        app_resp = self.client.post(
            f"/api/v1/procurement/requisitions/{req_id}/approve/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert app_resp.status_code == status.HTTP_200_OK
        assert app_resp.data["authorization_status"] == "approved"

        # Check fulfillment endpoint (derived)
        fulf_resp = self.client.get(
            f"/api/v1/procurement/requisitions/{req_id}/fulfillment/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert fulf_resp.status_code == status.HTTP_200_OK
        assert fulf_resp.data["fulfillment_position"] == "NOT_ORDERED"

        req_detail = self.client.get(
            f"/api/v1/procurement/requisitions/{req_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        req_item_id = req_detail.data["items"][0]["id"]

        # 5. Create Purchase Order with allocation
        po_resp = self.client.post(
            "/api/v1/procurement/orders/",
            {
                "vendor_id": vendor_id,
                "requisition_id": req_id,
                "items": [
                    {
                        "description": "Math Textbooks",
                        "quantity": "50.00",
                        "unit": "books",
                        "unit_price": "9.50",
                        "allocations": [
                            {
                                "requisition_item_id": req_item_id,
                                "allocated_quantity": "50.00",
                            }
                        ],
                    }
                ],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert po_resp.status_code == status.HTTP_201_CREATED
        order_id = po_resp.data["order_id"]

        # 6. Issue Purchase Order
        issue_resp = self.client.post(
            f"/api/v1/procurement/orders/{order_id}/issue/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert issue_resp.status_code == status.HTTP_200_OK
        assert issue_resp.data["status"] == "issued"
        assert issue_resp.data["payment_terms"] == "Net 30"

        po_detail = self.client.get(
            f"/api/v1/procurement/orders/{order_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        po_item_id = po_detail.data["items"][0]["id"]

        # Check delivery position before receipt
        pos_resp = self.client.get(
            f"/api/v1/procurement/orders/{order_id}/delivery-position/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert pos_resp.status_code == status.HTTP_200_OK
        assert pos_resp.data["delivery_position"] == "NOT_DELIVERED"

        # 7. Record Goods Receipt
        grn_resp = staff_client.post(
            "/api/v1/procurement/receipts/",
            {
                "purchase_order_id": order_id,
                "received_date": str(date.today()),
                "receipt_type": "goods",
                "items": [
                    {
                        "po_item_id": po_item_id,
                        "quantity_received": "50.00",
                    }
                ],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert grn_resp.status_code == status.HTTP_201_CREATED
        grn_id = grn_resp.data["receipt_id"]

        grn_detail = self.client.get(
            f"/api/v1/procurement/receipts/{grn_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        grn_item_id = grn_detail.data["items"][0]["id"]

        # 8. Inspect Goods Receipt
        insp_resp = staff_client.post(
            f"/api/v1/procurement/receipts/{grn_id}/inspect/",
            {
                "inspections": [
                    {
                        "grn_item_id": grn_item_id,
                        "quantity_accepted": "48.00",
                        "quantity_rejected": "2.00",
                        "rejection_reason": "Torn covers",
                    }
                ]
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert insp_resp.status_code == status.HTTP_200_OK
        assert insp_resp.data["is_fully_inspected"] is True
        assert insp_resp.data["has_rejections"] is True

        # Check updated delivery position (48/50 accepted -> PARTIALLY_DELIVERED)
        pos_resp2 = self.client.get(
            f"/api/v1/procurement/orders/{order_id}/delivery-position/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert pos_resp2.data["delivery_position"] == "PARTIALLY_DELIVERED"

        # 9. Explicitly close purchase order
        close_resp = self.client.post(
            f"/api/v1/procurement/orders/{order_id}/close/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert close_resp.status_code == status.HTTP_200_OK
        assert close_resp.data["status"] == "closed"

    def test_rbac_denial(self) -> None:
        """Member role cannot create purchase orders or approve requisitions."""
        member_client = APIClient()
        member_client.force_authenticate(user=self.member_user)

        # Member cannot create vendor
        v_resp = member_client.post(
            "/api/v1/procurement/vendors/",
            {"name": "Unauthorized Vendor"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert v_resp.status_code == status.HTTP_403_FORBIDDEN

        # Member cannot create purchase order
        po_resp = member_client.post(
            "/api/v1/procurement/orders/",
            {"vendor_id": str(uuid.uuid4())},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert po_resp.status_code == status.HTTP_403_FORBIDDEN

        # Staff cannot approve requisition (only owner/admin)
        staff_client = APIClient()
        staff_client.force_authenticate(user=self.staff_user)

        # Create requisition first
        pr_resp = self.client.post(
            "/api/v1/procurement/requisitions/",
            {
                "title": "Test PR",
                "items": [
                    {
                        "description": "Item",
                        "quantity": "1.00",
                        "unit_price": "10.00",
                    }
                ],
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        req_id = pr_resp.data["requisition_id"]
        self.client.post(
            f"/api/v1/procurement/requisitions/{req_id}/submit/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )

        app_resp = staff_client.post(
            f"/api/v1/procurement/requisitions/{req_id}/approve/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert app_resp.status_code == status.HTTP_403_FORBIDDEN

        # Member cannot return requisition (requires procurement:requisitions:create)
        ret_resp = member_client.post(
            f"/api/v1/procurement/requisitions/{req_id}/return/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert ret_resp.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_tenant_isolation(self) -> None:
        """Ensure entity in Org A is inaccessible from Org B context."""
        v_resp = self.client.post(
            "/api/v1/procurement/vendors/",
            {"name": "Org A Vendor"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        vendor_id = v_resp.data["vendor_id"]

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
                name="Org B Procurement",
                slug=f"org-b-{uuid.uuid4().hex[:6]}",
            )
        )

        # Accessing Org A vendor from Org B context returns 404
        cross_resp = self.client.get(
            f"/api/v1/procurement/vendors/{vendor_id}/",
            HTTP_X_ORGANIZATION_ID=str(org_b.organization_id),
        )
        assert cross_resp.status_code == status.HTTP_404_NOT_FOUND
