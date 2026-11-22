from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import (
    CategoryNotFoundError,
    InventoryError,
    OrganizationMismatchError,
)
from abren_one.modules.inventory.models import ItemCategory
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateItemCategoryInput:
    context: ExecutionContext
    name: str
    code: str
    description: str = ""
    parent_id: UUID | None = None


@dataclass(frozen=True)
class CreateItemCategoryResult:
    category_id: UUID
    name: str
    code: str
    parent_id: UUID | None


@transaction.atomic
def execute(data: CreateItemCategoryInput) -> CreateItemCategoryResult:
    """Create a new item category within the organization."""
    check_permission(data.context, "inventory:items:manage")

    if data.context.organization_id is None:
        raise InventoryError("Organization context is required.")

    if data.context.actor_id is None:
        raise InventoryError("Actor ID is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise InventoryError("Cannot create category for an inactive organization.")

    name = data.name.strip()
    if not name:
        raise InventoryError("Category name cannot be empty.")

    code = data.code.strip().upper()
    if not code:
        raise InventoryError("Category code cannot be empty.")

    if ItemCategory.objects.filter(organization_id=org.id, code=code).exists():
        raise InventoryError(f"Category with code '{code}' already exists in this organization.")

    parent = None
    if data.parent_id is not None:
        try:
            parent = ItemCategory.objects.get(id=data.parent_id)
        except ItemCategory.DoesNotExist as exc:
            raise CategoryNotFoundError("Parent category not found.") from exc

        if parent.organization_id != org.id:
            raise OrganizationMismatchError("Parent category does not belong to this organization.")

    category = ItemCategory.objects.create(
        organization_id=org.id,
        name=name,
        code=code,
        description=data.description.strip(),
        parent=parent,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="inventory.category.created",
        target_type="inventory.ItemCategory",
        target_id=category.id,
        correlation_id=data.context.correlation_id,
        metadata={"name": category.name, "code": category.code},
    )

    return CreateItemCategoryResult(
        category_id=category.id,
        name=category.name,
        code=category.code,
        parent_id=category.parent_id,
    )
