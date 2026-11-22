import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.modules.programs.application.commands.create_activity import (
    CreateActivityInput,
)
from abren_one.modules.programs.application.commands.create_activity import (
    execute as create_activity,
)
from abren_one.modules.programs.application.commands.create_program import (
    CreateProgramInput,
)
from abren_one.modules.programs.application.commands.create_program import (
    execute as create_program,
)
from abren_one.modules.programs.application.commands.create_project import (
    CreateProjectInput,
)
from abren_one.modules.programs.application.commands.create_project import (
    execute as create_project,
)
from abren_one.modules.programs.application.commands.update_activity import (
    UpdateActivityInput,
)
from abren_one.modules.programs.application.commands.update_activity import (
    execute as update_activity,
)
from abren_one.modules.programs.application.commands.update_program import (
    UpdateProgramInput,
)
from abren_one.modules.programs.application.commands.update_program import (
    execute as update_program,
)
from abren_one.modules.programs.application.commands.update_project import (
    UpdateProjectInput,
)
from abren_one.modules.programs.application.commands.update_project import (
    execute as update_project,
)
from abren_one.modules.programs.application.queries.get_activity import (
    execute as get_activity,
)
from abren_one.modules.programs.application.queries.get_program import (
    execute as get_program,
)
from abren_one.modules.programs.application.queries.get_project import (
    execute as get_project,
)
from abren_one.modules.programs.application.queries.list_activities import (
    execute as list_activities,
)
from abren_one.modules.programs.application.queries.list_programs import (
    execute as list_programs,
)
from abren_one.modules.programs.application.queries.list_projects import (
    execute as list_projects,
)
from abren_one.modules.programs.interfaces.api.v1.serializers import (
    ActivityDetailResponseSerializer,
    ActivitySummaryResponseSerializer,
    CreateActivityRequestSerializer,
    CreateProgramRequestSerializer,
    CreateProjectRequestSerializer,
    ProgramDetailResponseSerializer,
    ProgramSummaryResponseSerializer,
    ProjectDetailResponseSerializer,
    ProjectSummaryResponseSerializer,
    UpdateActivityRequestSerializer,
    UpdateProgramRequestSerializer,
    UpdateProjectRequestSerializer,
)
from abren_one.platform.authorization.permissions import require_permission
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class ProgramListCreateView(APIView):
    """List and create programs for the active organization (§7.2)."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("programs:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("programs:view")(),
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

        programs = list_programs(
            organization_id=request.org_context.organization_id,
            limit=limit,
            offset=offset,
        )
        return Response(ProgramSummaryResponseSerializer(programs, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateProgramRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_program(
            CreateProgramInput(
                context=context,
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
                start_date=serializer.validated_data.get("start_date"),
                end_date=serializer.validated_data.get("end_date"),
            )
        )

        return Response({"program_id": str(result.program_id)}, status=status.HTTP_201_CREATED)


class ProgramDetailView(APIView):
    """Retrieve or update details for a specific program (§7.2)."""

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("programs:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("programs:view")(),
        ]

    def get(self, request: Request, program_id: uuid.UUID) -> Response:
        result = get_program(
            organization_id=request.org_context.organization_id,
            program_id=program_id,
        )
        return Response(ProgramDetailResponseSerializer(result).data)

    def patch(self, request: Request, program_id: uuid.UUID) -> Response:
        serializer = UpdateProgramRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = update_program(
            UpdateProgramInput(
                context=context,
                program_id=program_id,
                name=serializer.validated_data.get("name"),
                description=serializer.validated_data.get("description"),
                status=serializer.validated_data.get("status"),
                start_date=serializer.validated_data.get("start_date"),
                end_date=serializer.validated_data.get("end_date"),
            )
        )
        return Response({"program_id": str(result.program_id), "status": result.status})


class ProjectListCreateView(APIView):
    """List and create projects for the active organization."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("projects:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("programs:view")(),
        ]

    def get(self, request: Request) -> Response:
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

        projects = list_projects(
            organization_id=request.org_context.organization_id,
            program_id=program_id,
            limit=limit,
            offset=offset,
        )
        return Response(ProjectSummaryResponseSerializer(projects, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateProjectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_project(
            CreateProjectInput(
                context=context,
                program_id=serializer.validated_data["program_id"],
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
                budget_currency=serializer.validated_data.get("budget_currency", "USD"),
            )
        )
        return Response({"project_id": str(result.project_id)}, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    """Retrieve or update details for a specific project."""

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("projects:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("programs:view")(),
        ]

    def get(self, request: Request, project_id: uuid.UUID) -> Response:
        project = get_project(
            organization_id=request.org_context.organization_id,
            project_id=project_id,
        )
        return Response(ProjectDetailResponseSerializer(project).data)

    def patch(self, request: Request, project_id: uuid.UUID) -> Response:
        serializer = UpdateProjectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = update_project(
            UpdateProjectInput(
                context=context,
                project_id=project_id,
                name=serializer.validated_data.get("name"),
                description=serializer.validated_data.get("description"),
                status=serializer.validated_data.get("status"),
                budget_currency=serializer.validated_data.get("budget_currency"),
            )
        )
        return Response({"project_id": str(result.project_id), "status": result.status})


class ActivityListCreateView(APIView):
    """List and create activities for the active organization."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("activities:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("programs:view")(),
        ]

    def get(self, request: Request) -> Response:
        project_id_raw = request.query_params.get("project_id")
        project_id = uuid.UUID(project_id_raw) if project_id_raw else None
        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        activities = list_activities(
            organization_id=request.org_context.organization_id,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )
        return Response(ActivitySummaryResponseSerializer(activities, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateActivityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = create_activity(
            CreateActivityInput(
                context=context,
                project_id=serializer.validated_data["project_id"],
                name=serializer.validated_data["name"],
                due_date=serializer.validated_data.get("due_date"),
            )
        )
        return Response({"activity_id": str(result.activity_id)}, status=status.HTTP_201_CREATED)


class ActivityDetailView(APIView):
    """Retrieve or update details for a specific activity."""

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("activities:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("programs:view")(),
        ]

    def get(self, request: Request, activity_id: uuid.UUID) -> Response:
        activity = get_activity(
            organization_id=request.org_context.organization_id,
            activity_id=activity_id,
        )
        return Response(ActivityDetailResponseSerializer(activity).data)

    def patch(self, request: Request, activity_id: uuid.UUID) -> Response:
        serializer = UpdateActivityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = build_execution_context(request)
        result = update_activity(
            UpdateActivityInput(
                context=context,
                activity_id=activity_id,
                name=serializer.validated_data.get("name"),
                status=serializer.validated_data.get("status"),
                due_date=serializer.validated_data.get("due_date"),
            )
        )
        return Response({"activity_id": str(result.activity_id), "status": result.status})
