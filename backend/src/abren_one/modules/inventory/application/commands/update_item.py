from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import (
    CategoryNotFoundError,
    InventoryError,
    ItemNotFoundError,
    OrganizationMismatchError,
)
from abren_one.modules.inventory.domain.policies import validate_non_negative
from abren_one.modules.inventory.domain.value_objects import ItemType
from abren_one.modules.inventory.models import Item, ItemCategory
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateItemInput:
    context: ExecutionContext
    item_id: UUID
    name: str | None = None
    description: str | None = None
    category_id: UUID | None = None
    unit_of_measure: str | None = None
    item_type: str | None = None
    track_batches: bool | None = None
    track_expiry: bool | None = None
    reorder_threshold: Decimal | None = None
    default_unit_cost: Decimal | None = None
    is_active: bool | None = None


@dataclass(frozen=True)
class UpdateItemResult:
    item_id: UUID
    item_code: str
    name: str
    is_active: bool


@transaction.atomic
def execute(data: UpdateItemInput) -> UpdateItemResult:
    """Update master details of an inventory item."""
    check_permission(data.context, "inventory:items:manage")

    if data.context.organization_id is None:
        raise InventoryError("Organization context is required.")

    if data.context.actor_id is None:
        raise InventoryError("Actor ID is required.")

    try:
        item = Item.objects.select_for_update().get(
            id=data.item_id,
            organization_id=data.context.organization_id,
        )
    except Item.DoesNotExist as exc:
        raise ItemNotFoundError("Item not found in this organization.") from exc

    if data.name is not None:
        name = data.name.strip()
        if not name:
            raise InventoryError("Item name cannot be empty.")
        item.name = name

    if data.description is not None:
        item.description = data.description.strip()

    if data.category_id is not None:
        try:
            category = ItemCategory.objects.get(id=data.category_id)
        except ItemCategory.DoesNotExist as exc:
            raise CategoryNotFoundError("Category not found.") from exc

        if category.organization_id != item.organization_id:
            raise OrganizationMismatchError("Category does not belong to this organization.")
        item.category = category

    if data.unit_of_measure is not None:
        item.unit_of_measure = data.unit_of_measure.strip() or "each"

    if data.item_type is not None:
        valid_types = {t.value for t in ItemType}
        if data.item_type not in valid_types:
            raise InventoryError(f"Invalid item type '{data.item_type}'. Must be one of {sorted(valid_types)}.")
        item.item_type = data.item_type

    if data.track_batches is not None:
        item.track_batches = data.track_batches

    if data.track_expiry is not None:
        item.track_expiry = data.track_expiry

    if data.reorder_threshold is not None:
        validate_non_negative(data.reorder_threshold, "Reorder threshold")
        item.reorder_threshold = data.reorder_threshold

    if data.default_unit_cost is not None:
        validate_non_negative(data.default_unit_cost, "Default unit cost")
        item.default_unit_cost = data.default_unit_cost

    if data.is_active is not None:
        item.is_active = data.is_active

    item.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=item.organization_id,
        action="inventory.item.updated",
        target_type="inventory.Item",
        target_id=item.id,
        correlation_id=data.context.correlation_id,
        metadata={"item_code": item.item_code, "is_active": item.is_active},
    )

    return UpdateItemResult(
        item_id=item.id,
        item_code=item.item_code,
        name=item.name,
        is_active=item.is_active,
    )
