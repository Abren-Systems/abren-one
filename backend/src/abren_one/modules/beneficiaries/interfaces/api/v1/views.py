import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    RecordServiceDeliveryInput,
)
from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    execute as record_service_delivery,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    RegisterBeneficiaryInput,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    execute as register_beneficiary,
)
from abren_one.modules.beneficiaries.application.commands.update_beneficiary import (
    UpdateBeneficiaryInput,
)
from abren_one.modules.beneficiaries.application.commands.update_beneficiary import (
    execute as update_beneficiary,
)
from abren_one.modules.beneficiaries.application.queries.get_beneficiary import (
    execute as get_beneficiary,
)
from abren_one.modules.beneficiaries.application.queries.get_service_delivery import (
    execute as get_service_delivery,
)
from abren_one.modules.beneficiaries.application.queries.list_beneficiaries import (
    execute as list_beneficiaries,
)
from abren_one.modules.beneficiaries.application.queries.list_service_deliveries import (
    execute as list_service_deliveries,
)
from abren_one.modules.beneficiaries.interfaces.api.v1.serializers import (
    BeneficiaryDetailResponseSerializer,
    BeneficiarySummaryResponseSerializer,
    RecordServiceDeliveryRequestSerializer,
    RegisterBeneficiaryRequestSerializer,
    ServiceDeliveryResponseSerializer,
    UpdateBeneficiaryRequestSerializer,
)
from abren_one.platform.authorization.permissions import require_permission
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class BeneficiaryListCreateView(APIView):
    """List and register beneficiaries within the active organization (§7.2)."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("beneficiaries:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("beneficiaries:view")(),
        ]

    def get(self, request: Request) -> Response:
        status_param = request.query_params.get("status")
        type_param = request.query_params.get("beneficiary_type")
        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        beneficiaries = list_beneficiaries(
            organization_id=request.org_context.organization_id,
            status=status_param,
            beneficiary_type=type_param,
            limit=limit,
            offset=offset,
        )
        return Response(BeneficiarySummaryResponseSerializer(beneficiaries, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = RegisterBeneficiaryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = register_beneficiary(
            RegisterBeneficiaryInput(
                context=context,
                beneficiary_type=serializer.validated_data.get("beneficiary_type", "individual"),
                identification_number=serializer.validated_data.get("identification_number", ""),
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
                household_name=serializer.validated_data.get("household_name", ""),
                date_of_birth=serializer.validated_data.get("date_of_birth"),
                gender=serializer.validated_data.get("gender", "unspecified"),
                vulnerability_level=serializer.validated_data.get("vulnerability_level", "medium"),
                contact_phone=serializer.validated_data.get("contact_phone", ""),
                contact_address=serializer.validated_data.get("contact_address", ""),
                notes=serializer.validated_data.get("notes", ""),
            )
        )

        return Response({"beneficiary_id": str(result.beneficiary_id)}, status=status.HTTP_201_CREATED)


class BeneficiaryDetailView(APIView):
    """Retrieve or update details for a specific beneficiary."""

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("beneficiaries:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("beneficiaries:view")(),
        ]

    def get(self, request: Request, beneficiary_id: uuid.UUID) -> Response:
        beneficiary = get_beneficiary(
            organization_id=request.org_context.organization_id,
            beneficiary_id=beneficiary_id,
        )
        return Response(BeneficiaryDetailResponseSerializer(beneficiary).data)

    def patch(self, request: Request, beneficiary_id: uuid.UUID) -> Response:
        serializer = UpdateBeneficiaryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = update_beneficiary(
            UpdateBeneficiaryInput(
                context=context,
                beneficiary_id=beneficiary_id,
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                household_name=serializer.validated_data.get("household_name"),
                status=serializer.validated_data.get("status"),
                vulnerability_level=serializer.validated_data.get("vulnerability_level"),
                contact_phone=serializer.validated_data.get("contact_phone"),
                contact_address=serializer.validated_data.get("contact_address"),
                notes=serializer.validated_data.get("notes"),
            )
        )

        return Response({"beneficiary_id": str(result.beneficiary_id), "status": result.status})


class ServiceDeliveryListCreateView(APIView):
    """List and record service deliveries within the active organization."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("service_deliveries:record")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("service_deliveries:view")(),
        ]

    def get(self, request: Request) -> Response:
        beneficiary_id_raw = request.query_params.get("beneficiary_id")
        beneficiary_id = uuid.UUID(beneficiary_id_raw) if beneficiary_id_raw else None
        program_id_raw = request.query_params.get("program_id")
        program_id = uuid.UUID(program_id_raw) if program_id_raw else None

        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        deliveries = list_service_deliveries(
            organization_id=request.org_context.organization_id,
            beneficiary_id=beneficiary_id,
            program_id=program_id,
            limit=limit,
            offset=offset,
        )
        return Response(ServiceDeliveryResponseSerializer(deliveries, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = RecordServiceDeliveryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = record_service_delivery(
            RecordServiceDeliveryInput(
                context=context,
                beneficiary_id=serializer.validated_data["beneficiary_id"],
                service_type=serializer.validated_data["service_type"],
                delivery_date=serializer.validated_data["delivery_date"],
                quantity=serializer.validated_data.get("quantity"),
                unit=serializer.validated_data.get("unit", "unit"),
                program_id=serializer.validated_data.get("program_id"),
                activity_id=serializer.validated_data.get("activity_id"),
                notes=serializer.validated_data.get("notes", ""),
                status=serializer.validated_data.get("status", "delivered"),
            )
        )

        return Response({"delivery_id": str(result.delivery_id)}, status=status.HTTP_201_CREATED)


class ServiceDeliveryDetailView(APIView):
    """Retrieve details for a specific service delivery."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("service_deliveries:view"),
    ]

    def get(self, request: Request, delivery_id: uuid.UUID) -> Response:
        delivery = get_service_delivery(
            organization_id=request.org_context.organization_id,
            delivery_id=delivery_id,
        )
        return Response(ServiceDeliveryResponseSerializer(delivery).data)
