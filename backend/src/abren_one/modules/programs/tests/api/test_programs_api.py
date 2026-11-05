import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.modules.programs.models import Program
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestProgramsAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="prog_user", password="secretpassword")
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
                name="Active Org",
                slug="active-org",
            )
        )
        self.org_id = self.org_result.organization_id

    def test_create_and_list_programs(self) -> None:
        # Create program
        create_resp = self.client.post(
            "/api/v1/programs/",
            {"name": "Clean Water Project", "description": "Well construction"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        program_id = create_resp.data["program_id"]

        # List programs
        list_resp = self.client.get(
            "/api/v1/programs/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["name"] == "Clean Water Project"

        # Detail program
        detail_resp = self.client.get(
            f"/api/v1/programs/{program_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["name"] == "Clean Water Project"

    def test_cross_tenant_program_isolation(self) -> None:
        """Negative cross-tenant test (§5.6):

        User scoped to Org A cannot see programs belonging to Org B.
        """
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        other_org_result = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Other Org",
                slug="other-prog-org",
            )
        )
        other_prog = Program.objects.create(
            organization_id=other_org_result.organization_id,
            name="Confidential Org B Initiative",
        )

        # 1. Listing as Org A does not include Org B's program
        list_resp = self.client.get(
            "/api/v1/programs/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        names = [p["name"] for p in list_resp.data]
        assert "Confidential Org B Initiative" not in names

        # 2. Direct detail access to Org B's program as Org A returns 404 (Fail-closed §5.4)
        detail_resp = self.client.get(
            f"/api/v1/programs/{other_prog.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_404_NOT_FOUND
