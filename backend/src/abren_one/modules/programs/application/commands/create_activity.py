from dataclasses import dataclass
from datetime import date
from uuid import UUID

from django.db import transaction

from abren_one.modules.programs.domain.exceptions import (
    ProgramError,
    ProjectNotFoundError,
)
from abren_one.modules.programs.domain.value_objects import (
    ActivityStatus,
    ProjectStatus,
)
from abren_one.modules.programs.models import Activity, Project
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateActivityInput:
    context: ExecutionContext
    project_id: UUID
    name: str
    due_date: date | None = None


@dataclass(frozen=True)
class CreateActivityResult:
    activity_id: UUID


@transaction.atomic
def execute(data: CreateActivityInput) -> CreateActivityResult:
    """Create a new activity within a project and active organization (§6.2)."""
    check_permission(data.context, "activities:manage")

    if data.context.organization_id is None:
        raise ProgramError("Organization context is required.")

    try:
        project = Project.objects.get(
            id=data.project_id,
            organization_id=data.context.organization_id,
        )
    except Project.DoesNotExist as exc:
        raise ProjectNotFoundError(f"Project {data.project_id} not found.") from exc

    if project.status == ProjectStatus.COMPLETED.value:
        raise ProgramError("Cannot create activities under a completed project.")

    activity = Activity.objects.create(
        organization_id=data.context.organization_id,
        project=project,
        name=data.name,
        status=ActivityStatus.PENDING.value,
        due_date=data.due_date,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="activity.created",
        target_type="programs.Activity",
        target_id=activity.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"name": activity.name, "project_id": str(project.id)},
    )

    return CreateActivityResult(activity_id=activity.id)
