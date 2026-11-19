from dataclasses import dataclass
from datetime import date
from uuid import UUID

from django.db import transaction

from abren_one.modules.programs.domain.exceptions import (
    InvalidProgramTransitionError,
    ProgramError,
    ProgramNotFoundError,
)
from abren_one.modules.programs.domain.policies import can_transition_program_status
from abren_one.modules.programs.domain.value_objects import ProgramStatus
from abren_one.modules.programs.models import Program
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateProgramInput:
    context: ExecutionContext
    program_id: UUID
    name: str | None = None
    description: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None


@dataclass(frozen=True)
class UpdateProgramResult:
    program_id: UUID
    status: str


@transaction.atomic
def execute(data: UpdateProgramInput) -> UpdateProgramResult:
    """Update program details or transition its status (§6.2)."""
    if data.context.organization_id is None:
        raise ProgramError("Organization context is required.")

    try:
        program = Program.objects.select_for_update().get(
            id=data.program_id,
            organization_id=data.context.organization_id,
        )
    except Program.DoesNotExist as exc:
        raise ProgramNotFoundError(f"Program {data.program_id} not found.") from exc

    if data.status is not None and data.status != program.status:
        try:
            target_status = ProgramStatus(data.status)
        except ValueError as exc:
            raise ProgramError(f"Invalid program status: '{data.status}'.") from exc

        current_status = ProgramStatus(program.status)
        if not can_transition_program_status(current_status, target_status):
            raise InvalidProgramTransitionError(
                f"Cannot transition program from '{program.status}' to '{data.status}'."
            )
        program.status = target_status.value

    if data.name is not None and data.name != program.name:
        if (
            Program.objects.filter(
                organization_id=data.context.organization_id,
                name=data.name,
            )
            .exclude(id=program.id)
            .exists()
        ):
            raise ProgramError(f"A program named '{data.name}' already exists in this organization.")
        program.name = data.name

    if data.description is not None:
        program.description = data.description

    if data.start_date is not None:
        program.start_date = data.start_date

    if data.end_date is not None:
        program.end_date = data.end_date

    if program.start_date and program.end_date and program.end_date < program.start_date:
        raise ProgramError("Program end date must be on or after start date.")

    program.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="program.updated",
        target_type="programs.Program",
        target_id=program.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"name": program.name, "status": program.status},
    )

    return UpdateProgramResult(program_id=program.id, status=program.status)
