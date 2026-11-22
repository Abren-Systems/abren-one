from dataclasses import dataclass
from datetime import date
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.public import get_organization
from abren_one.modules.programs.domain.exceptions import ProgramError
from abren_one.modules.programs.domain.value_objects import ProgramStatus
from abren_one.modules.programs.models import Program
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateProgramInput:
    context: ExecutionContext
    name: str
    description: str = ""
    start_date: date | None = None
    end_date: date | None = None


@dataclass(frozen=True)
class CreateProgramResult:
    program_id: UUID


@transaction.atomic
def execute(data: CreateProgramInput) -> CreateProgramResult:
    """Create a new program within the active organization (§6.2).

    Cross-module interaction:
    Validates that the organization exists and is active using the Organizations
    module's public query `get_organization` via `public.py`.
    """
    check_permission(data.context, "programs:manage")

    if data.context.organization_id is None:
        raise ProgramError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise ProgramError("Cannot create a program for an inactive or suspended organization.")

    if Program.objects.filter(organization_id=org.id, name=data.name).exists():
        raise ProgramError(f"A program named '{data.name}' already exists in this organization.")

    program = Program.objects.create(
        organization_id=org.id,
        name=data.name,
        description=data.description,
        status=ProgramStatus.ACTIVE.value,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="program.created",
        target_type="programs.Program",
        target_id=program.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"name": program.name},
    )

    return CreateProgramResult(program_id=program.id)
