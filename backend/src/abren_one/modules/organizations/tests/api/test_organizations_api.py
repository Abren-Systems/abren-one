import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from abren_one.modules.organizations.models import Branch, Membership, Organization

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationsAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_user", password="secretpassword")
        self.client.force_authenticate(user=self.user)

    def test_provision_organization_endpoint(self) -> None:
        response = self.client.post(
            "/api/v1/organizations/",
            {"name": "New NGO", "slug": "new-ngo"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "organization_id" in response.data
        assert response.data["slug"] == "new-ngo"

        # Verify the user is now the active owner of the new organization
        org_id = response.data["organization_id"]
        assert Membership.objects.filter(organization_id=org_id, user=self.user, role="owner").exists()

    def test_get_current_organization_success(self) -> None:
        org = Organization.objects.create(name="My Org", slug="my-org")
        Membership.objects.create(organization=org, user=self.user, role="owner", status="active")

        response = self.client.get(
            "/api/v1/organizations/current/",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "My Org"
        assert response.data["slug"] == "my-org"

    def test_missing_organization_header_is_denied(self) -> None:
        response = self.client.get("/api/v1/organizations/current/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "X-Organization-ID" in str(response.data)

    def test_malformed_organization_header_is_denied(self) -> None:
        response = self.client.get(
            "/api/v1/organizations/current/",
            HTTP_X_ORGANIZATION_ID="not-a-valid-uuid",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_tenant_isolation_non_member_denied(self) -> None:
        """Negative cross-tenant test (§5.6):

        User A cannot access Org B's data when User A is not a member.
        """
        other_user = User.objects.create_user(username="other", password="secretpassword")
        other_org = Organization.objects.create(name="Other Org", slug="other-org")
        Membership.objects.create(organization=other_org, user=other_user, role="owner", status="active")

        # Self tries to access other_org
        response = self.client.get(
            "/api/v1/organizations/current/",
            HTTP_X_ORGANIZATION_ID=str(other_org.id),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "membership" in str(response.data).lower()

    def test_cross_tenant_branch_isolation(self) -> None:
        """Negative cross-tenant test (§5.6):

        Branches belonging to Org B are never returned to a caller scoped to Org A.
        """
        org_a = Organization.objects.create(name="Org A", slug="org-a")
        Membership.objects.create(organization=org_a, user=self.user, role="owner", status="active")
        Branch.objects.create(organization=org_a, name="Branch A", code="BA-1")

        org_b = Organization.objects.create(name="Org B", slug="org-b")
        Branch.objects.create(organization=org_b, name="Secret Branch B", code="BB-1")

        # Request branches as Org A
        response = self.client.get(
            "/api/v1/organizations/branches/",
            HTTP_X_ORGANIZATION_ID=str(org_a.id),
        )
        assert response.status_code == status.HTTP_200_OK
        branch_codes = [b["code"] for b in response.data]
        assert "BA-1" in branch_codes
        assert "BB-1" not in branch_codes

    def test_non_admin_cannot_add_members(self) -> None:
        org = Organization.objects.create(name="Role Org", slug="role-org")
        Membership.objects.create(organization=org, user=self.user, role="member", status="active")
        new_user = User.objects.create_user(username="newbie", password="password")

        response = self.client.post(
            "/api/v1/organizations/members/",
            {"user_id": str(new_user.id), "role": "member"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
