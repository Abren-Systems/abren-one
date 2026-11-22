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

    def test_list_user_organizations_endpoint(self) -> None:
        org1 = Organization.objects.create(name="Alpha Org", slug="alpha-org")
        org2 = Organization.objects.create(name="Beta Org", slug="beta-org")
        Membership.objects.create(organization=org1, user=self.user, role="admin", status="active")
        Membership.objects.create(organization=org2, user=self.user, role="staff", status="active")

        # Third org where user is not a member
        Organization.objects.create(name="Gamma Org", slug="gamma-org")

        response = self.client.get("/api/v1/organizations/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        names = [o["name"] for o in response.data]
        assert "Alpha Org" in names
        assert "Beta Org" in names
        assert "Gamma Org" not in names

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

    def test_non_admin_cannot_mutate_memberships(self) -> None:
        org = Organization.objects.create(name="Role Org Mutate", slug="role-org-mutate")
        Membership.objects.create(organization=org, user=self.user, role="member", status="active")
        target_user = User.objects.create_user(username="target_user", password="password")
        target_membership = Membership.objects.create(
            organization=org,
            user=target_user,
            role="member",
            status="active",
        )

        # Suspend attempt by regular member is denied
        suspend_resp = self.client.post(
            f"/api/v1/organizations/members/{target_membership.id}/suspend/",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert suspend_resp.status_code == status.HTTP_403_FORBIDDEN

        # Activate attempt by regular member is denied
        activate_resp = self.client.post(
            f"/api/v1/organizations/members/{target_membership.id}/activate/",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert activate_resp.status_code == status.HTTP_403_FORBIDDEN

        # Revoke attempt by regular member is denied
        revoke_resp = self.client.post(
            f"/api/v1/organizations/members/{target_membership.id}/revoke/",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert revoke_resp.status_code == status.HTTP_403_FORBIDDEN

    def test_branch_response_includes_organization_id(self) -> None:
        org = Organization.objects.create(name="Branch Org", slug="branch-org")
        Membership.objects.create(organization=org, user=self.user, role="owner", status="active")
        Branch.objects.create(organization=org, name="Main Branch", code="MB-1")

        response = self.client.get(
            "/api/v1/organizations/branches/",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["organization_id"] == str(org.id)

    def test_provision_duplicate_slug_returns_400(self) -> None:
        Organization.objects.create(name="Existing NGO", slug="existing-ngo")
        response = self.client.post(
            "/api/v1/organizations/",
            {"name": "Another NGO", "slug": "existing-ngo"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in str(response.data)

    def test_create_and_list_departments(self) -> None:
        org = Organization.objects.create(name="Dept Org", slug="dept-api-org")
        Membership.objects.create(organization=org, user=self.user, role="owner", status="active")
        branch = Branch.objects.create(organization=org, name="HQ Branch", code="HQ-1", is_headquarters=True)

        # 1. Create department with branch
        resp = self.client.post(
            "/api/v1/organizations/departments/",
            {"name": "Human Resources", "code": "HR", "branch_id": str(branch.id)},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        dept_id = resp.data["department_id"]

        # 2. List departments
        list_resp = self.client.get(
            "/api/v1/organizations/departments/",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["name"] == "Human Resources"
        assert list_resp.data[0]["code"] == "HR"
        assert list_resp.data[0]["branch_id"] == str(branch.id)

        # 3. Retrieve department detail
        detail_resp = self.client.get(
            f"/api/v1/organizations/departments/{dept_id}/",
            HTTP_X_ORGANIZATION_ID=str(org.id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["id"] == str(dept_id)
        assert detail_resp.data["name"] == "Human Resources"

    def test_cross_tenant_department_isolation(self) -> None:
        org_a = Organization.objects.create(name="Org A Dept", slug="org-a-dept")
        Membership.objects.create(organization=org_a, user=self.user, role="owner", status="active")

        other_user = User.objects.create_user(username="dept_other", password="secretpassword")
        org_b = Organization.objects.create(name="Org B Dept", slug="org-b-dept")
        Membership.objects.create(organization=org_b, user=other_user, role="owner", status="active")

        from abren_one.modules.organizations.models import Department

        dept_b = Department.objects.create(organization=org_b, name="Confidential B", code="CONF")

        # Org A cannot see Org B's department in list
        list_resp = self.client.get(
            "/api/v1/organizations/departments/",
            HTTP_X_ORGANIZATION_ID=str(org_a.id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 0

        # Org A cannot retrieve Org B's department by ID (fails with 404)
        detail_resp = self.client.get(
            f"/api/v1/organizations/departments/{dept_b.id}/",
            HTTP_X_ORGANIZATION_ID=str(org_a.id),
        )
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND
