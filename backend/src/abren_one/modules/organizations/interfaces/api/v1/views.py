import uuid

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
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
from abren_one.modules.organizations.application.exceptions import (
    CannotRevokeLastOwnerError,
    DuplicateMembershipError,
    MembershipNotFoundError,
    OrganizationError,
    OrganizationNotFoundError,
)
from abren_one.modules.organizations.application.queries.get_organization import (
    execute as get_organization,
)
from abren_one.modules.organizations.application.queries.list_branches import (
    execute as list_branches,
)
from abren_one.modules.organizations.application.queries.list_members import (
    execute as list_members,
)
from abren_one.modules.organizations.interfaces.api.v1.serializers import (
    AddMemberRequestSerializer,
    BranchResponseSerializer,
    CreateBranchRequestSerializer,
    CreateOrganizationRequestSerializer,
    MemberResponseSerializer,
    OrganizationResponseSerializer,
)
from abren_one.platform.authorization.permissions import require_role
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class ProvisionOrganizationView(APIView):
    """Initial organization provisioning (§5.2, §5.3).

    Requires authentication, but does NOT require prior organization context.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = CreateOrganizationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        try:
            result = create_organization(
                CreateOrganizationInput(
                    context=context,
                    name=serializer.validated_data["name"],
                    slug=serializer.validated_data["slug"],
                )
            )
        except OrganizationError as exc:
            raise ValidationError({"error": str(exc)}) from exc

        return Response(
            {"organization_id": str(result.organization_id), "slug": result.slug},
            status=status.HTTP_201_CREATED,
        )


class CurrentOrganizationDetailView(APIView):
    """Retrieve details for the active organization context (§5.3)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        try:
            result = get_organization(organization_id=request.org_context.organization_id)
        except OrganizationNotFoundError as exc:
            raise NotFound(str(exc)) from exc

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
        try:
            result = create_branch(
                CreateBranchInput(
                    context=context,
                    name=serializer.validated_data["name"],
                    code=serializer.validated_data["code"],
                    is_headquarters=serializer.validated_data.get("is_headquarters", False),
                )
            )
        except OrganizationError as exc:
            raise ValidationError({"error": str(exc)}) from exc

        return Response({"branch_id": str(result.branch_id)}, status=status.HTTP_201_CREATED)


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
        try:
            result = add_member(
                AddMemberInput(
                    context=context,
                    user_id=serializer.validated_data["user_id"],
                    role=serializer.validated_data["role"],
                )
            )
        except (DuplicateMembershipError, OrganizationError) as exc:
            raise ValidationError({"error": str(exc)}) from exc

        return Response({"membership_id": str(result.membership_id)}, status=status.HTTP_201_CREATED)


class ActivateMemberView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationContext, require_role("owner", "admin")]

    def post(self, request: Request, membership_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        try:
            result = activate_membership(ActivateMembershipInput(context=context, membership_id=membership_id))
        except MembershipNotFoundError as exc:
            raise NotFound(str(exc)) from exc
        except OrganizationError as exc:
            raise ValidationError({"error": str(exc)}) from exc

        return Response({"membership_id": str(result.membership_id), "status": result.status})


class SuspendMemberView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationContext, require_role("owner", "admin")]

    def post(self, request: Request, membership_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        try:
            result = suspend_membership(SuspendMembershipInput(context=context, membership_id=membership_id))
        except MembershipNotFoundError as exc:
            raise NotFound(str(exc)) from exc
        except OrganizationError as exc:
            raise ValidationError({"error": str(exc)}) from exc

        return Response({"membership_id": str(result.membership_id), "status": result.status})


class RevokeMemberView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationContext, require_role("owner", "admin")]

    def post(self, request: Request, membership_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        try:
            result = revoke_membership(RevokeMembershipInput(context=context, membership_id=membership_id))
        except MembershipNotFoundError as exc:
            raise NotFound(str(exc)) from exc
        except CannotRevokeLastOwnerError as exc:
            raise ValidationError({"error": str(exc)}) from exc
        except OrganizationError as exc:
            raise ValidationError({"error": str(exc)}) from exc

        return Response({"membership_id": str(result.membership_id), "status": "revoked"})
