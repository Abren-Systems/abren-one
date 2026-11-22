from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.programs.domain.exceptions import (
    ProgramError,
    ProgramNotFoundError,
)
from abren_one.modules.programs.domain.value_objects import (
    ProgramStatus,
    ProjectStatus,
)
from abren_one.modules.programs.models import Program, Project
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateProjectInput:
    context: ExecutionContext
    program_id: UUID
    name: str
    description: str = ""
    budget_currency: str = "USD"


@dataclass(frozen=True)
class CreateProjectResult:
    project_id: UUID


@transaction.atomic
def execute(data: CreateProjectInput) -> CreateProjectResult:
    """Create a new project within a program and the active organization (§6.2)."""
    check_permission(data.context, "projects:manage")

    if data.context.organization_id is None:
        raise ProgramError("Organization context is required.")

    try:
        program = Program.objects.get(
            id=data.program_id,
            organization_id=data.context.organization_id,
        )
    except Program.DoesNotExist as exc:
        raise ProgramNotFoundError(f"Program {data.program_id} not found.") from exc

    if program.status in {ProgramStatus.COMPLETED.value, ProgramStatus.ARCHIVED.value}:
        raise ProgramError(f"Cannot create project under program in '{program.status}' status.")

    if Project.objects.filter(program=program, name=data.name).exists():
        raise ProgramError(f"A project named '{data.name}' already exists in this program.")

    project = Project.objects.create(
        organization_id=data.context.organization_id,
        program=program,
        name=data.name,
        description=data.description,
        status=ProjectStatus.PLANNING.value,
        budget_currency=data.budget_currency,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="project.created",
        target_type="programs.Project",
        target_id=project.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"name": project.name, "program_id": str(program.id)},
    )

    return CreateProjectResult(project_id=project.id)
