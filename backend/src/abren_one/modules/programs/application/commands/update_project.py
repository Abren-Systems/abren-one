from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.programs.domain.exceptions import (
    InvalidProjectTransitionError,
    ProgramError,
    ProjectNotFoundError,
)
from abren_one.modules.programs.domain.policies import can_transition_project_status
from abren_one.modules.programs.domain.value_objects import ProjectStatus
from abren_one.modules.programs.models import Project
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateProjectInput:
    context: ExecutionContext
    project_id: UUID
    name: str | None = None
    description: str | None = None
    status: str | None = None
    budget_currency: str | None = None


@dataclass(frozen=True)
class UpdateProjectResult:
    project_id: UUID
    status: str


@transaction.atomic
def execute(data: UpdateProjectInput) -> UpdateProjectResult:
    """Update project details or transition its status (§6.2)."""
    check_permission(data.context, "projects:manage")

    if data.context.organization_id is None:
        raise ProgramError("Organization context is required.")

    try:
        project = Project.objects.select_for_update().get(
            id=data.project_id,
            organization_id=data.context.organization_id,
        )
    except Project.DoesNotExist as exc:
        raise ProjectNotFoundError(f"Project {data.project_id} not found.") from exc

    if data.status is not None and data.status != project.status:
        try:
            target_status = ProjectStatus(data.status)
        except ValueError as exc:
            raise ProgramError(f"Invalid project status: '{data.status}'.") from exc

        current_status = ProjectStatus(project.status)
        if not can_transition_project_status(current_status, target_status):
            raise InvalidProjectTransitionError(
                f"Cannot transition project from '{project.status}' to '{data.status}'."
            )
        project.status = target_status.value

    if data.name is not None and data.name != project.name:
        if (
            Project.objects.filter(
                program_id=project.program_id,
                name=data.name,
            )
            .exclude(id=project.id)
            .exists()
        ):
            raise ProgramError(f"A project named '{data.name}' already exists in this program.")
        project.name = data.name

    if data.description is not None:
        project.description = data.description

    if data.budget_currency is not None:
        project.budget_currency = data.budget_currency

    project.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="project.updated",
        target_type="programs.Project",
        target_id=project.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"name": project.name, "status": project.status},
    )

    return UpdateProjectResult(project_id=project.id, status=project.status)
