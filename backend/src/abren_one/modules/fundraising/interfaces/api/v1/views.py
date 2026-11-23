import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.modules.fundraising.application.commands.activate_grant import (
    ActivateGrantInput,
)
from abren_one.modules.fundraising.application.commands.activate_grant import (
    execute as activate_grant,
)
from abren_one.modules.fundraising.application.commands.award_grant import (
    AwardGrantInput,
)
from abren_one.modules.fundraising.application.commands.award_grant import (
    execute as award_grant,
)
from abren_one.modules.fundraising.application.commands.close_grant import (
    CloseGrantInput,
)
from abren_one.modules.fundraising.application.commands.close_grant import (
    execute as close_grant,
)
from abren_one.modules.fundraising.application.commands.create_donor import (
    CreateDonorInput,
)
from abren_one.modules.fundraising.application.commands.create_donor import (
    execute as create_donor,
)
from abren_one.modules.fundraising.application.commands.create_grant import (
    CreateGrantInput,
)
from abren_one.modules.fundraising.application.commands.create_grant import (
    execute as create_grant,
)
from abren_one.modules.fundraising.application.commands.record_donation import (
    RecordDonationInput,
)
from abren_one.modules.fundraising.application.commands.record_donation import (
    execute as record_donation,
)
from abren_one.modules.fundraising.application.queries.get_donor import (
    execute as get_donor,
)
from abren_one.modules.fundraising.application.queries.get_grant import (
    execute as get_grant,
)
from abren_one.modules.fundraising.application.queries.list_donations import (
    execute as list_donations,
)
from abren_one.modules.fundraising.application.queries.list_donors import (
    execute as list_donors,
)
from abren_one.modules.fundraising.application.queries.list_grants import (
    execute as list_grants,
)
from abren_one.modules.fundraising.interfaces.api.v1.serializers import (
    CreateDonorRequestSerializer,
    CreateGrantRequestSerializer,
    DonationResponseSerializer,
    DonorResponseSerializer,
    GrantResponseSerializer,
    RecordDonationRequestSerializer,
)
from abren_one.platform.authorization.permissions import require_permission
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class DonorListCreateView(APIView):
    """List and create donors for the active organization (§7.2)."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("donors:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("donors:view")(),
        ]

    def get(self, request: Request) -> Response:
        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        donors = list_donors(
            organization_id=request.org_context.organization_id,
            limit=limit,
            offset=offset,
        )
        return Response(DonorResponseSerializer(donors, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateDonorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_donor(
            CreateDonorInput(
                context=context,
                name=serializer.validated_data["name"],
                donor_type=serializer.validated_data.get("donor_type", "individual"),
                email=serializer.validated_data.get("email", ""),
                phone=serializer.validated_data.get("phone", ""),
            )
        )

        return Response({"donor_id": str(result.donor_id)}, status=status.HTTP_201_CREATED)


class DonorDetailView(APIView):
    """Retrieve donor details within the active organization (§7.2)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("donors:view"),
    ]

    def get(self, request: Request, donor_id: uuid.UUID) -> Response:
        donor = get_donor(donor_id=donor_id, organization_id=request.org_context.organization_id)
        return Response(DonorResponseSerializer(donor).data)


class GrantListCreateView(APIView):
    """List and create grants for the active organization (§7.2)."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("grants:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("grants:view")(),
        ]

    def get(self, request: Request) -> Response:
        donor_id_raw = request.query_params.get("donor_id")
        donor_id = uuid.UUID(donor_id_raw) if donor_id_raw else None
        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        grants = list_grants(
            organization_id=request.org_context.organization_id,
            donor_id=donor_id,
            limit=limit,
            offset=offset,
        )
        return Response(GrantResponseSerializer(grants, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateGrantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_grant(
            CreateGrantInput(
                context=context,
                donor_id=serializer.validated_data["donor_id"],
                title=serializer.validated_data["title"],
                reference_code=serializer.validated_data["reference_code"],
                total_amount=serializer.validated_data["total_amount"],
                currency=serializer.validated_data.get("currency", "USD"),
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
                program_id=serializer.validated_data.get("program_id"),
            )
        )

        return Response({"grant_id": str(result.grant_id)}, status=status.HTTP_201_CREATED)


class GrantDetailView(APIView):
    """Retrieve grant details within the active organization (§7.2)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("grants:view"),
    ]

    def get(self, request: Request, grant_id: uuid.UUID) -> Response:
        grant = get_grant(grant_id=grant_id, organization_id=request.org_context.organization_id)
        return Response(GrantResponseSerializer(grant).data)


class AwardGrantView(APIView):
    """Transition a proposed grant to awarded status (§7.2)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("grants:manage"),
    ]

    def post(self, request: Request, grant_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        notes = request.data.get("notes", "") if isinstance(request.data, dict) else ""
        result = award_grant(AwardGrantInput(context=context, grant_id=grant_id, notes=notes))
        return Response({"grant_id": str(result.grant_id), "status": result.status}, status=status.HTTP_200_OK)


class ActivateGrantView(APIView):
    """Transition an awarded grant to active status (§7.2)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("grants:manage"),
    ]

    def post(self, request: Request, grant_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        notes = request.data.get("notes", "") if isinstance(request.data, dict) else ""
        result = activate_grant(ActivateGrantInput(context=context, grant_id=grant_id, notes=notes))
        return Response({"grant_id": str(result.grant_id), "status": result.status}, status=status.HTTP_200_OK)


class CloseGrantView(APIView):
    """Transition a grant to closed status (§7.2)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("grants:manage"),
    ]

    def post(self, request: Request, grant_id: uuid.UUID) -> Response:
        context = build_execution_context(request)
        reason = request.data.get("reason", "") if isinstance(request.data, dict) else ""
        result = close_grant(CloseGrantInput(context=context, grant_id=grant_id, reason=reason))
        return Response({"grant_id": str(result.grant_id), "status": result.status}, status=status.HTTP_200_OK)


class DonationListCreateView(APIView):
    """List and record donations for the active organization (§7.2)."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("donations:record")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("donations:view")(),
        ]

    def get(self, request: Request) -> Response:
        donor_id_raw = request.query_params.get("donor_id")
        donor_id = uuid.UUID(donor_id_raw) if donor_id_raw else None
        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        donations = list_donations(
            organization_id=request.org_context.organization_id,
            donor_id=donor_id,
            limit=limit,
            offset=offset,
        )
        return Response(DonationResponseSerializer(donations, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = RecordDonationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = record_donation(
            RecordDonationInput(
                context=context,
                donor_id=serializer.validated_data["donor_id"],
                amount=serializer.validated_data["amount"],
                currency=serializer.validated_data.get("currency", "USD"),
                payment_method=serializer.validated_data.get("payment_method", "bank_transfer"),
                reference=serializer.validated_data.get("reference", ""),
                grant_id=serializer.validated_data.get("grant_id"),
                program_id=serializer.validated_data.get("program_id"),
                received_at=serializer.validated_data.get("received_at"),
            )
        )

        return Response({"donation_id": str(result.donation_id)}, status=status.HTTP_201_CREATED)
