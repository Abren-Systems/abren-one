from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.programs.domain.exceptions import ProjectNotFoundError
from abren_one.modules.programs.models import Project


@dataclass(frozen=True)
class GetProjectResult:
    id: UUID
    organization_id: UUID
    program_id: UUID
    name: str
    description: str
    status: str
    budget_currency: str


def execute(*, organization_id: UUID, project_id: UUID) -> GetProjectResult:
    """Retrieve a project by ID within the active organization."""
    try:
        project = Project.objects.get(id=project_id, organization_id=organization_id)
    except Project.DoesNotExist as exc:
        raise ProjectNotFoundError(f"Project {project_id} not found.") from exc

    return GetProjectResult(
        id=project.id,
        organization_id=project.organization_id,
        program_id=project.program_id,
        name=project.name,
        description=project.description,
        status=project.status,
        budget_currency=project.budget_currency,
    )
