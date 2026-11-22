from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import (
    CategoryNotFoundError,
    InventoryError,
    OrganizationMismatchError,
)
from abren_one.modules.inventory.domain.policies import validate_non_negative
from abren_one.modules.inventory.domain.value_objects import ItemType
from abren_one.modules.inventory.models import Item, ItemCategory
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateItemInput:
    context: ExecutionContext
    category_id: UUID
    item_code: str
    name: str
    description: str = ""
    unit_of_measure: str = "each"
    item_type: str = ItemType.CONSUMABLE.value
    track_batches: bool = False
    track_expiry: bool = False
    reorder_threshold: Decimal = Decimal("0.00")
    default_unit_cost: Decimal = Decimal("0.00")


@dataclass(frozen=True)
class CreateItemResult:
    item_id: UUID
    item_code: str
    name: str
    unit_of_measure: str
    item_type: str
    is_active: bool


@transaction.atomic
def execute(data: CreateItemInput) -> CreateItemResult:
    """Create a new stock-tracked item in the organization's catalog."""
    check_permission(data.context, "inventory:items:manage")

    if data.context.organization_id is None:
        raise InventoryError("Organization context is required.")

    if data.context.actor_id is None:
        raise InventoryError("Actor ID is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise InventoryError("Cannot create item for an inactive organization.")

    name = data.name.strip()
    if not name:
        raise InventoryError("Item name cannot be empty.")

    item_code = data.item_code.strip().upper()
    if not item_code:
        raise InventoryError("Item code cannot be empty.")

    valid_types = {t.value for t in ItemType}
    if data.item_type not in valid_types:
        raise InventoryError(f"Invalid item type '{data.item_type}'. Must be one of {sorted(valid_types)}.")

    validate_non_negative(data.reorder_threshold, "Reorder threshold")
    validate_non_negative(data.default_unit_cost, "Default unit cost")

    if Item.objects.filter(organization_id=org.id, item_code=item_code).exists():
        raise InventoryError(f"Item with code '{item_code}' already exists in this organization.")

    try:
        category = ItemCategory.objects.get(id=data.category_id)
    except ItemCategory.DoesNotExist as exc:
        raise CategoryNotFoundError("Item category not found.") from exc

    if category.organization_id != org.id:
        raise OrganizationMismatchError("Item category does not belong to this organization.")

    item = Item.objects.create(
        organization_id=org.id,
        category=category,
        item_code=item_code,
        name=name,
        description=data.description.strip(),
        unit_of_measure=data.unit_of_measure.strip() or "each",
        item_type=data.item_type,
        track_batches=data.track_batches,
        track_expiry=data.track_expiry,
        reorder_threshold=data.reorder_threshold,
        default_unit_cost=data.default_unit_cost,
        is_active=True,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="inventory.item.created",
        target_type="inventory.Item",
        target_id=item.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "item_code": item.item_code,
            "name": item.name,
            "category_id": str(category.id),
            "item_type": item.item_type,
        },
    )

    return CreateItemResult(
        item_id=item.id,
        item_code=item.item_code,
        name=item.name,
        unit_of_measure=item.unit_of_measure,
        item_type=item.item_type,
        is_active=item.is_active,
    )
