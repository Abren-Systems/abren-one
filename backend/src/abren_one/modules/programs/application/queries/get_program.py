from dataclasses import dataclass
from datetime import date
from uuid import UUID

from abren_one.modules.programs.domain.exceptions import ProgramNotFoundError
from abren_one.modules.programs.models import Program


@dataclass(frozen=True)
class GetProgramResult:
    id: UUID
    organization_id: UUID
    name: str
    description: str
    status: str
    is_active: bool
    start_date: date | None = None
    end_date: date | None = None


def execute(*, organization_id: UUID, program_id: UUID) -> GetProgramResult:
    """Retrieve a program by ID within the active organization."""
    try:
        prog = Program.objects.get(id=program_id, organization_id=organization_id)
    except Program.DoesNotExist as exc:
        raise ProgramNotFoundError(f"Program {program_id} not found.") from exc

    return GetProgramResult(
        id=prog.id,
        organization_id=prog.organization_id,
        name=prog.name,
        description=prog.description,
        status=prog.status,
        is_active=prog.is_active,
        start_date=prog.start_date,
        end_date=prog.end_date,
    )
