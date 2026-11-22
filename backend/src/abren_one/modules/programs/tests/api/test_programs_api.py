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
            {
                "name": "Clean Water Project",
                "description": "Well construction",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            },
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
        assert detail_resp.data["start_date"] == "2026-01-01"
        assert detail_resp.data["end_date"] == "2026-12-31"

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

    def test_patch_program(self) -> None:
        prog = Program.objects.create(organization_id=self.org_id, name="Original Program")
        resp = self.client.patch(
            f"/api/v1/programs/{prog.id}/",
            {"name": "Patched Program", "status": "completed"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "completed"

        prog.refresh_from_db()
        assert prog.name == "Patched Program"
        assert prog.status == "completed"

    def test_project_api_lifecycle(self) -> None:
        prog = Program.objects.create(organization_id=self.org_id, name="Project Host Program")

        # Create project
        create_resp = self.client.post(
            "/api/v1/programs/projects/",
            {
                "program_id": str(prog.id),
                "name": "School Construction",
                "description": "Building classrooms",
                "budget_currency": "USD",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project_id = create_resp.data["project_id"]

        # List projects
        list_resp = self.client.get(
            f"/api/v1/programs/projects/?program_id={prog.id}",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["id"] == str(project_id)
        assert list_resp.data[0]["name"] == "School Construction"

        # Detail project
        detail_resp = self.client.get(
            f"/api/v1/programs/projects/{project_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["name"] == "School Construction"
        assert detail_resp.data["status"] == "planning"

        # Patch project
        patch_resp = self.client.patch(
            f"/api/v1/programs/projects/{project_id}/",
            {"status": "in_progress"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert patch_resp.status_code == status.HTTP_200_OK
        assert patch_resp.data["status"] == "in_progress"

    def test_activity_api_lifecycle(self) -> None:
        from abren_one.modules.programs.models import Project

        prog = Program.objects.create(organization_id=self.org_id, name="Activity Host Program")
        proj = Project.objects.create(
            organization_id=self.org_id,
            program=prog,
            name="Host Project",
        )

        # Create activity
        create_resp = self.client.post(
            "/api/v1/programs/activities/",
            {
                "project_id": str(proj.id),
                "name": "Site Survey",
                "due_date": "2026-06-30",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        activity_id = create_resp.data["activity_id"]

        # List activities
        list_resp = self.client.get(
            f"/api/v1/programs/activities/?project_id={proj.id}",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1
        assert list_resp.data[0]["id"] == str(activity_id)

        # Detail activity
        detail_resp = self.client.get(
            f"/api/v1/programs/activities/{activity_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["name"] == "Site Survey"
        assert detail_resp.data["status"] == "pending"

        # Patch activity
        patch_resp = self.client.patch(
            f"/api/v1/programs/activities/{activity_id}/",
            {"status": "in_progress"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert patch_resp.status_code == status.HTTP_200_OK
        assert patch_resp.data["status"] == "in_progress"

    def test_cross_tenant_project_and_activity_isolation(self) -> None:
        from abren_one.modules.programs.models import Activity, Project

        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        other_org = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Other Secret Org",
                slug="secret-prog-org",
            )
        )
        other_prog = Program.objects.create(organization_id=other_org.organization_id, name="Secret Prog")
        other_proj = Project.objects.create(
            organization_id=other_org.organization_id,
            program=other_prog,
            name="Secret Project",
        )
        other_act = Activity.objects.create(
            organization_id=other_org.organization_id,
            project=other_proj,
            name="Secret Activity",
        )

        # Org A requests Org B's project -> 404
        proj_resp = self.client.get(
            f"/api/v1/programs/projects/{other_proj.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert proj_resp.status_code == status.HTTP_404_NOT_FOUND

        # Org A requests Org B's activity -> 404
        act_resp = self.client.get(
            f"/api/v1/programs/activities/{other_act.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert act_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_rbac_permission_denial_for_member_role(self) -> None:
        from rest_framework.test import APIClient

        from abren_one.modules.organizations.public import AddMemberInput, add_member

        member_user = User.objects.create_user(username="prog_member", password="password123")
        admin_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.user.id,
            organization_id=self.org_id,
            correlation_id=uuid.uuid4(),
            actor_role="owner",
        )
        add_member(
            AddMemberInput(
                context=admin_ctx,
                user_id=member_user.id,
                role="member",
            )
        )

        member_client = APIClient()
        member_client.force_authenticate(user=member_user)

        # Member can view programs
        resp_view = member_client.get(
            "/api/v1/programs/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp_view.status_code == status.HTTP_200_OK

        # Member cannot create program (403 Forbidden)
        resp_create = member_client.post(
            "/api/v1/programs/",
            {
                "name": "Member Unauthorized Program",
                "description": "Should fail",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp_create.status_code == status.HTTP_403_FORBIDDEN
