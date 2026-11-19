from dataclasses import dataclass
from datetime import date
from uuid import UUID

from django.db import transaction

from abren_one.modules.programs.domain.exceptions import (
    ActivityNotFoundError,
    InvalidActivityTransitionError,
    ProgramError,
)
from abren_one.modules.programs.domain.policies import can_transition_activity_status
from abren_one.modules.programs.domain.value_objects import ActivityStatus
from abren_one.modules.programs.models import Activity
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateActivityInput:
    context: ExecutionContext
    activity_id: UUID
    name: str | None = None
    status: str | None = None
    due_date: date | None = None


@dataclass(frozen=True)
class UpdateActivityResult:
    activity_id: UUID
    status: str


@transaction.atomic
def execute(data: UpdateActivityInput) -> UpdateActivityResult:
    """Update activity details or transition its status (§6.2)."""
    if data.context.organization_id is None:
        raise ProgramError("Organization context is required.")

    try:
        activity = Activity.objects.select_for_update().get(
            id=data.activity_id,
            organization_id=data.context.organization_id,
        )
    except Activity.DoesNotExist as exc:
        raise ActivityNotFoundError(f"Activity {data.activity_id} not found.") from exc

    if data.status is not None and data.status != activity.status:
        try:
            target_status = ActivityStatus(data.status)
        except ValueError as exc:
            raise ProgramError(f"Invalid activity status: '{data.status}'.") from exc

        current_status = ActivityStatus(activity.status)
        if not can_transition_activity_status(current_status, target_status):
            raise InvalidActivityTransitionError(
                f"Cannot transition activity from '{activity.status}' to '{data.status}'."
            )
        activity.status = target_status.value

    if data.name is not None:
        activity.name = data.name

    if data.due_date is not None:
        activity.due_date = data.due_date

    activity.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="activity.updated",
        target_type="programs.Activity",
        target_id=activity.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"name": activity.name, "status": activity.status},
    )

    return UpdateActivityResult(activity_id=activity.id, status=activity.status)
