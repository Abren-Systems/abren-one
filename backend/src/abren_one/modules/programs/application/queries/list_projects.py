from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.programs.models import Project


@dataclass(frozen=True)
class ProjectSummaryResult:
    id: UUID
    organization_id: UUID
    program_id: UUID
    name: str
    status: str
    budget_currency: str


def execute(
    *,
    organization_id: UUID,
    program_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[ProjectSummaryResult]:
    """List projects for an organization, optionally filtered by program."""
    qs = Project.objects.filter(organization_id=organization_id)
    if program_id is not None:
        qs = qs.filter(program_id=program_id)
    qs = qs.order_by("name")[offset : offset + limit]

    return [
        ProjectSummaryResult(
            id=p.id,
            organization_id=p.organization_id,
            program_id=p.program_id,
            name=p.name,
            status=p.status,
            budget_currency=p.budget_currency,
        )
        for p in qs
    ]
