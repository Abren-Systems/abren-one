from dataclasses import dataclass
from datetime import date
from uuid import UUID

from abren_one.modules.programs.models import Activity


@dataclass(frozen=True)
class ActivitySummaryResult:
    id: UUID
    organization_id: UUID
    project_id: UUID
    name: str
    status: str
    due_date: date | None


def execute(*, organization_id: UUID, project_id: UUID | None = None) -> list[ActivitySummaryResult]:
    """List activities for an organization, optionally filtered by project."""
    qs = Activity.objects.filter(organization_id=organization_id)
    if project_id is not None:
        qs = qs.filter(project_id=project_id)
    qs = qs.order_by("created_at")

    return [
        ActivitySummaryResult(
            id=a.id,
            organization_id=a.organization_id,
            project_id=a.project_id,
            name=a.name,
            status=a.status,
            due_date=a.due_date,
        )
        for a in qs
    ]
