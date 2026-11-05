from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.domain.exceptions import OrganizationError
from abren_one.modules.organizations.models import Branch, Department, Organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateDepartmentInput:
    context: ExecutionContext
    name: str
    code: str
    branch_id: UUID | None = None


@dataclass(frozen=True)
class CreateDepartmentResult:
    department_id: UUID


@transaction.atomic
def execute(data: CreateDepartmentInput) -> CreateDepartmentResult:
    """Create a department within the active organization."""
    assert data.context.organization_id is not None, "Organization context is required."

    org = Organization.objects.get(id=data.context.organization_id)
    if Department.objects.filter(organization=org, code=data.code).exists():
        raise OrganizationError(f"Department with code '{data.code}' already exists in this organization.")

    branch = None
    if data.branch_id:
        branch = Branch.objects.get(id=data.branch_id, organization=org)

    department = Department.objects.create(
        organization=org,
        branch=branch,
        name=data.name,
        code=data.code,
        is_active=True,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="department.created",
        target_type="organizations.Department",
        target_id=department.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"code": department.code, "name": department.name},
    )

    return CreateDepartmentResult(department_id=department.id)
