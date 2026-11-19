from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.organizations.domain.exceptions import DepartmentNotFoundError
from abren_one.modules.organizations.models import Department


@dataclass(frozen=True)
class GetDepartmentResult:
    id: UUID
    organization_id: UUID
    branch_id: UUID | None
    name: str
    code: str
    is_active: bool


def execute(*, organization_id: UUID, department_id: UUID) -> GetDepartmentResult:
    """Retrieve a department by ID within the active organization."""
    try:
        dept = Department.objects.get(id=department_id, organization_id=organization_id)
    except Department.DoesNotExist as exc:
        raise DepartmentNotFoundError(f"Department {department_id} not found.") from exc

    return GetDepartmentResult(
        id=dept.id,
        organization_id=dept.organization_id,
        branch_id=dept.branch_id,
        name=dept.name,
        code=dept.code,
        is_active=dept.is_active,
    )
