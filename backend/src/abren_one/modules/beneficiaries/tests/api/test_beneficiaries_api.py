import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from abren_one.modules.beneficiaries.models import Beneficiary, ServiceDelivery
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestBeneficiariesAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="ben_officer", password="secretpassword")
        self.client.force_authenticate(user=self.user)

        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.user.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        self.org_result = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Refugee Relief",
                slug=f"refugee-relief-{uuid.uuid4().hex[:6]}",
            )
        )
        self.org_id = self.org_result.organization_id

    def test_register_and_list_beneficiaries(self) -> None:
        resp = self.client.post(
            "/api/v1/beneficiaries/",
            {
                "beneficiary_type": "individual",
                "identification_number": "REF-001",
                "first_name": "Tariq",
                "last_name": "Al-Mansour",
                "gender": "male",
                "vulnerability_level": "high",
                "contact_phone": "+251922334455",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        ben_id = resp.data["beneficiary_id"]

        # Detail
        detail_resp = self.client.get(
            f"/api/v1/beneficiaries/{ben_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["display_name"] == "Tariq Al-Mansour"
        assert detail_resp.data["vulnerability_level"] == "high"

        # List
        list_resp = self.client.get(
            "/api/v1/beneficiaries/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["id"] == ben_id

        # Patch
        patch_resp = self.client.patch(
            f"/api/v1/beneficiaries/{ben_id}/",
            {"vulnerability_level": "critical"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert patch_resp.status_code == status.HTTP_200_OK

        detail_resp2 = self.client.get(
            f"/api/v1/beneficiaries/{ben_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp2.data["vulnerability_level"] == "critical"

    def test_record_and_list_service_deliveries(self) -> None:
        ben = Beneficiary.objects.create(
            organization_id=self.org_id,
            first_name="Sara",
            last_name="Ibrahim",
            status="active",
        )

        resp = self.client.post(
            "/api/v1/beneficiaries/deliveries/",
            {
                "beneficiary_id": str(ben.id),
                "service_type": "medical_support",
                "delivery_date": "2026-04-15",
                "quantity": "2.00",
                "unit": "consultations",
                "notes": "Post-natal checkup",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        deliv_id = resp.data["delivery_id"]

        # Detail
        detail_resp = self.client.get(
            f"/api/v1/beneficiaries/deliveries/{deliv_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["service_type"] == "medical_support"
        assert detail_resp.data["beneficiary_name"] == "Sara Ibrahim"

        # List
        list_resp = self.client.get(
            "/api/v1/beneficiaries/deliveries/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["id"] == deliv_id

    def test_cross_tenant_beneficiary_isolation(self) -> None:
        """Negative cross-tenant test (§5.6):

        User scoped to Org A cannot see beneficiaries or deliveries belonging to Org B.
        """
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        other_org = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Other Org",
                slug=f"other-org-{uuid.uuid4().hex[:6]}",
            )
        )
        other_ben = Beneficiary.objects.create(
            organization_id=other_org.organization_id,
            first_name="Secret",
            last_name="Beneficiary",
        )
        other_deliv = ServiceDelivery.objects.create(
            organization_id=other_org.organization_id,
            beneficiary=other_ben,
            service_type="food_assistance",
            delivery_date="2026-05-01",
            quantity="10.00",
        )

        # 1. Listing beneficiaries as Org A does not include Org B's beneficiary
        list_resp = self.client.get(
            "/api/v1/beneficiaries/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 0

        # 2. Detail access to Org B beneficiary as Org A returns 404
        detail_resp = self.client.get(
            f"/api/v1/beneficiaries/{other_ben.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

        # 3. Listing deliveries as Org A does not include Org B's delivery
        deliv_list = self.client.get(
            "/api/v1/beneficiaries/deliveries/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert deliv_list.status_code == status.HTTP_200_OK
        assert len(deliv_list.data) == 0

        # 4. Detail access to Org B delivery as Org A returns 404
        deliv_detail = self.client.get(
            f"/api/v1/beneficiaries/deliveries/{other_deliv.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert deliv_detail.status_code == status.HTTP_404_NOT_FOUND
