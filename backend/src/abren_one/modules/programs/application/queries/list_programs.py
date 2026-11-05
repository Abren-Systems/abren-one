from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.programs.models import Program


@dataclass(frozen=True)
class ProgramSummaryResult:
    id: UUID
    organization_id: UUID
    name: str
    status: str
    is_active: bool


def execute(*, organization_id: UUID) -> list[ProgramSummaryResult]:
    """List all programs for the active organization."""
    programs = Program.objects.filter(organization_id=organization_id).order_by("name")
    return [
        ProgramSummaryResult(
            id=p.id,
            organization_id=p.organization_id,
            name=p.name,
            status=p.status,
            is_active=p.is_active,
        )
        for p in programs
    ]
