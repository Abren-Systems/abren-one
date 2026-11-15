import uuid

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.modules.programs.application.commands.create_program import (
    CreateProgramInput,
)
from abren_one.modules.programs.application.commands.create_program import (
    execute as create_program,
)
from abren_one.modules.programs.application.exceptions import (
    ProgramError,
    ProgramNotFoundError,
)
from abren_one.modules.programs.application.queries.get_program import (
    execute as get_program,
)
from abren_one.modules.programs.application.queries.list_programs import (
    execute as list_programs,
)
from abren_one.modules.programs.interfaces.api.v1.serializers import (
    CreateProgramRequestSerializer,
    ProgramDetailResponseSerializer,
    ProgramSummaryResponseSerializer,
)
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class ProgramListCreateView(APIView):
    """List and create programs for the active organization (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        programs = list_programs(organization_id=request.org_context.organization_id)
        return Response(ProgramSummaryResponseSerializer(programs, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateProgramRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        try:
            result = create_program(
                CreateProgramInput(
                    context=context,
                    name=serializer.validated_data["name"],
                    description=serializer.validated_data.get("description", ""),
                )
            )
        except ProgramError as exc:
            raise ValidationError({"error": str(exc)}) from exc

        return Response({"program_id": str(result.program_id)}, status=status.HTTP_201_CREATED)


class ProgramDetailView(APIView):
    """Retrieve details for a specific program (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request, program_id: uuid.UUID) -> Response:
        try:
            result = get_program(
                organization_id=request.org_context.organization_id,
                program_id=program_id,
            )
        except ProgramNotFoundError as exc:
            raise NotFound(str(exc)) from exc

        return Response(ProgramDetailResponseSerializer(result).data)
