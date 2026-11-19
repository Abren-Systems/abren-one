from dataclasses import dataclass
from datetime import date
from uuid import UUID

from abren_one.modules.programs.domain.exceptions import ActivityNotFoundError
from abren_one.modules.programs.models import Activity


@dataclass(frozen=True)
class GetActivityResult:
    id: UUID
    organization_id: UUID
    project_id: UUID
    name: str
    status: str
    due_date: date | None


def execute(*, organization_id: UUID, activity_id: UUID) -> GetActivityResult:
    """Retrieve an activity by ID within the active organization."""
    try:
        activity = Activity.objects.get(id=activity_id, organization_id=organization_id)
    except Activity.DoesNotExist as exc:
        raise ActivityNotFoundError(f"Activity {activity_id} not found.") from exc

    return GetActivityResult(
        id=activity.id,
        organization_id=activity.organization_id,
        project_id=activity.project_id,
        name=activity.name,
        status=activity.status,
        due_date=activity.due_date,
    )
