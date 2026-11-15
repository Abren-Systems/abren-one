import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from abren_one.modules.fundraising.models import Donation, Donor, Grant
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestFundraisingAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="fundraiser_api", password="secretpassword")
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
                name="Charity Plus",
                slug=f"charity-plus-{uuid.uuid4().hex[:6]}",
            )
        )
        self.org_id = self.org_result.organization_id

    def test_create_and_list_donors(self) -> None:
        resp = self.client.post(
            "/api/v1/fundraising/donors/",
            {
                "name": "Global Giving",
                "donor_type": "foundation",
                "email": "info@globalgiving.org",
                "phone": "+1234567890",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        donor_id = resp.data["donor_id"]

        # Detail
        detail_resp = self.client.get(
            f"/api/v1/fundraising/donors/{donor_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["name"] == "Global Giving"
        assert detail_resp.data["donor_type"] == "foundation"

        # List
        list_resp = self.client.get(
            "/api/v1/fundraising/donors/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["id"] == donor_id

    def test_create_and_get_grant(self) -> None:
        donor = Donor.objects.create(
            organization_id=self.org_id,
            name="Gates Foundation",
            donor_type="foundation",
        )
        resp = self.client.post(
            "/api/v1/fundraising/grants/",
            {
                "donor_id": str(donor.id),
                "title": "Global Health Grant",
                "reference_code": "GHG-2026-01",
                "total_amount": "500000.00",
                "currency": "USD",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        grant_id = resp.data["grant_id"]

        detail_resp = self.client.get(
            f"/api/v1/fundraising/grants/{grant_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["title"] == "Global Health Grant"
        assert detail_resp.data["reference_code"] == "GHG-2026-01"

    def test_record_and_list_donations(self) -> None:
        donor = Donor.objects.create(
            organization_id=self.org_id,
            name="Individual Supporter",
            donor_type="individual",
        )
        resp = self.client.post(
            "/api/v1/fundraising/donations/",
            {
                "donor_id": str(donor.id),
                "amount": "1500.00",
                "currency": "USD",
                "payment_method": "credit_card",
                "reference": "TXN-12345",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        donation_id = resp.data["donation_id"]

        list_resp = self.client.get(
            "/api/v1/fundraising/donations/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["id"] == donation_id
        assert list_resp.data[0]["donor_name"] == "Individual Supporter"

    def test_cross_tenant_donor_isolation(self) -> None:
        """Negative cross-tenant test (§5.6):

        User scoped to Org A cannot see donors belonging to Org B.
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
        Donor.objects.create(
            organization_id=other_org.organization_id,
            name="Secret Org B Donor",
        )

        # Listing as Org A does not include Org B's donor
        list_resp = self.client.get(
            "/api/v1/fundraising/donors/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 0

    def test_cross_tenant_grant_isolation(self) -> None:
        """Negative cross-tenant test (§5.6):

        User scoped to Org A cannot see grants belonging to Org B.
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
                name="Other Org 2",
                slug=f"other-org2-{uuid.uuid4().hex[:6]}",
            )
        )
        other_donor = Donor.objects.create(
            organization_id=other_org.organization_id,
            name="Org B Donor",
        )
        other_grant = Grant.objects.create(
            organization_id=other_org.organization_id,
            donor=other_donor,
            title="Confidential Grant",
            reference_code="CONF-01",
            total_amount="100000.00",
            start_date="2026-01-01",
            end_date="2026-12-31",
        )

        # 1. Listing as Org A does not include Org B grant
        list_resp = self.client.get(
            "/api/v1/fundraising/grants/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 0

        # 2. Directly retrieving Org B grant via Org A context returns 404
        detail_resp = self.client.get(
            f"/api/v1/fundraising/grants/{other_grant.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_cross_tenant_donation_isolation(self) -> None:
        """Negative cross-tenant test (§5.6):

        User scoped to Org A cannot see donations belonging to Org B.
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
                name="Other Org 3",
                slug=f"other-org3-{uuid.uuid4().hex[:6]}",
            )
        )
        other_donor = Donor.objects.create(
            organization_id=other_org.organization_id,
            name="Org B Donor 3",
        )
        Donation.objects.create(
            organization_id=other_org.organization_id,
            donor=other_donor,
            amount="500.00",
            received_at="2026-01-01T12:00:00Z",
        )

        list_resp = self.client.get(
            "/api/v1/fundraising/donations/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 0

    def test_missing_tenant_header_fails_closed(self) -> None:
        """Fail closed when X-Organization-ID header is missing (§5.4)."""
        resp = self.client.get("/api/v1/fundraising/donors/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert "X-Organization-ID" in str(resp.data)
