import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.modules.organizations.application.commands.activate_membership import (
    ActivateMembershipInput,
)
from abren_one.modules.organizations.application.commands.activate_membership import (
    execute as activate_membership,
)
from abren_one.modules.organizations.application.commands.add_member import (
    AddMemberInput,
)
from abren_one.modules.organizations.application.commands.add_member import (
    execute as add_member,
)
from abren_one.modules.organizations.application.commands.create_branch import (
    CreateBranchInput,
)
from abren_one.modules.organizations.application.commands.create_branch import (
    execute as create_branch,
)
from abren_one.modules.organizations.application.commands.create_department import (
    CreateDepartmentInput,
)
from abren_one.modules.organizations.application.commands.create_department import (
    execute as create_department,
)
from abren_one.modules.organizations.application.commands.create_organization import (
    CreateOrganizationInput,
)
from abren_one.modules.organizations.application.commands.create_organization import (
    execute as create_organization,
)
from abren_one.modules.organizations.application.commands.revoke_membership import (
    RevokeMembershipInput,
)
from abren_one.modules.organizations.application.commands.revoke_membership import (
    execute as revoke_membership,
)
from abren_one.modules.organizations.application.commands.suspend_membership import (
    SuspendMembershipInput,
)
from abren_one.modules.organizations.application.commands.suspend_membership import (
    execute as suspend_membership,
)
from abren_one.modules.organizations.application.queries.get_department import (
    execute as get_department,
)
from abren_one.modules.organizations.application.queries.get_organization import (
    execute as get_organization,
)
from abren_one.modules.organizations.application.queries.list_branches import (
    execute as list_branches,
)
from abren_one.modules.organizations.application.queries.list_departments import (
    execute as list_departments,
)
from abren_one.modules.organizations.application.queries.list_members import (
    execute as list_members,
)
from abren_one.modules.organizations.application.queries.list_user_organizations import (
    execute as list_user_organizations,
)
from abren_one.modules.organizations.interfaces.api.v1.serializers import (
    AddMemberRequestSerializer,
    BranchResponseSerializer,
    CreateBranchRequestSerializer,
    CreateDepartmentRequestSerializer,
    CreateOrganizationRequestSerializer,
    DepartmentResponseSerializer,
    MemberResponseSerializer,
    OrganizationResponseSerializer,
    UserOrganizationResponseSerializer,
)
from abren_one.platform.authorization.permissions import require_role
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class ProvisionOrganizationView(APIView):
    """Initial organization provisioning and user organizations listing (§5.2, §5.3).

    Requires authentication, but does NOT require prior organization context.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        orgs = list_user_organizations(user_id=request.user.id)
        return Response(
            UserOrganizationResponseSerializer(orgs, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = CreateOrganizationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_organization(
            CreateOrganizationInput(
                context=context,
                name=serializer.validated_data["name"],
                slug=serializer.validated_data["slug"],
            )
        )

        return Response(
            {"organization_id": str(result.organization_id), "slug": result.slug},
            status=status.HTTP_201_CREATED,
        )


class CurrentOrganizationDetailView(APIView):
    """Retrieve details for the active organization context (§5.3)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        result = get_organization(organization_id=request.org_context.organization_id)
        return Response(OrganizationResponseSerializer(result).data)


class BranchListCreateView(APIView):
    """List or create branches in the active organization."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        branches = list_branches(organization_id=request.org_context.organization_id)
        return Response(BranchResponseSerializer(branches, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateBranchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_branch(
            CreateBranchInput(
                context=context,
                name=serializer.validated_data["name"],
                code=serializer.validated_data["code"],
                is_headquarters=serializer.validated_data.get("is_headquarters", False),
            )
        )

        return Response({"branch_id": str(result.branch_id)}, status=status.HTTP_201_CREATED)


class DepartmentListCreateView(APIView):
    """List or create departments in the active organization."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        branch_id_raw = request.query_params.get("branch_id")
        branch_id = uuid.UUID(branch_id_raw) if branch_id_raw else None
        departments = list_departments(
            organization_id=request.org_context.organization_id,
            branch_id=branch_id,
        )
        return Response(DepartmentResponseSerializer(departments, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateDepartmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_department(
            CreateDepartmentInput(
                context=context,
                name=serializer.validated_data["name"],
                code=serializer.validated_data["code"],
                branch_id=serializer.validated_data.get("branch_id"),
            )
        )

        return Response({"department_id": str(result.department_id)}, status=status.HTTP_201_CREATED)


class DepartmentDetailView(APIView):
    """Retrieve a department by ID within the active organization."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request, department_id: uuid.UUID) -> Response:
        dept = get_department(
            organization_id=request.org_context.organization_id,
            department_id=department_id,
        )
        return Response(DepartmentResponseSerializer(dept).data)


class MemberListCreateView(APIView):
    """List or add members in the active organization."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get_permissions(self):
        perms = [IsAuthenticated(), HasOrganizationContext()]
        if self.request and self.request.method == "POST":
            perms.append(require_role("owner", "admin")())
        return perms

    def get(self, request: Request) -> Response:
        members = list_members(organization_id=request.org_context.organization_id)
        return Response(MemberResponseSerializer(members, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = AddMemberRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = add_member(
            AddMemberInput(
                context=context,
                user_id=serializer.validated_data["user_id"],
                role=serializer.validated_data["role"],
            )
        )

        return Response({"membership_id": str(result.membership_id)}, status=status.HTTP_201_CREATED)


class ActivateMemberView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationContext, require_role("owner", "admin")]

    def post(self, request: Request, membership_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        result = activate_membership(ActivateMembershipInput(context=context, membership_id=membership_id))
        return Response({"membership_id": str(result.membership_id), "status": result.status})


class SuspendMemberView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationContext, require_role("owner", "admin")]

    def post(self, request: Request, membership_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        result = suspend_membership(SuspendMembershipInput(context=context, membership_id=membership_id))
        return Response({"membership_id": str(result.membership_id), "status": result.status})


class RevokeMemberView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationContext, require_role("owner", "admin")]

    def post(self, request: Request, membership_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        result = revoke_membership(RevokeMembershipInput(context=context, membership_id=membership_id))
        return Response({"membership_id": str(result.membership_id), "status": "revoked"})
