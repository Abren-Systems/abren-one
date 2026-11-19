from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.domain.exceptions import (
    BranchNotFoundError,
    OrganizationError,
    OrganizationNotFoundError,
)
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
    if data.context.organization_id is None:
        raise OrganizationError("Organization context is required.")

    try:
        org = Organization.objects.get(id=data.context.organization_id)
    except Organization.DoesNotExist as exc:
        raise OrganizationNotFoundError(f"Organization {data.context.organization_id} not found.") from exc

    if Department.objects.filter(organization=org, code=data.code).exists():
        raise OrganizationError(f"Department with code '{data.code}' already exists in this organization.")

    branch = None
    if data.branch_id:
        try:
            branch = Branch.objects.get(id=data.branch_id, organization=org)
        except Branch.DoesNotExist as exc:
            raise BranchNotFoundError(f"Branch {data.branch_id} not found in this organization.") from exc

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
