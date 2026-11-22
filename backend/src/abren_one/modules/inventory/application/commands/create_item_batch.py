from dataclasses import dataclass
from datetime import date
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    ItemNotFoundError,
)
from abren_one.modules.inventory.models import Item, ItemBatch
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateItemBatchInput:
    context: ExecutionContext
    item_id: UUID
    batch_number: str
    manufacture_date: date | None = None
    expiry_date: date | None = None


@dataclass(frozen=True)
class CreateItemBatchResult:
    batch_id: UUID
    item_id: UUID
    batch_number: str
    expiry_date: date | None


@transaction.atomic
def execute(data: CreateItemBatchInput) -> CreateItemBatchResult:
    """Register a new batch/lot for an item."""
    check_permission(data.context, "inventory:items:manage")

    if data.context.organization_id is None:
        raise InventoryError("Organization context is required.")

    if data.context.actor_id is None:
        raise InventoryError("Actor ID is required.")

    try:
        item = Item.objects.get(
            id=data.item_id,
            organization_id=data.context.organization_id,
        )
    except Item.DoesNotExist as exc:
        raise ItemNotFoundError("Item not found in this organization.") from exc

    batch_num = data.batch_number.strip()
    if not batch_num:
        raise InventoryError("Batch number cannot be empty.")

    if ItemBatch.objects.filter(item=item, batch_number=batch_num).exists():
        raise InventoryError(f"Batch '{batch_num}' already exists for item '{item.item_code}'.")

    if data.manufacture_date and data.expiry_date and data.expiry_date < data.manufacture_date:
        raise InventoryError("Batch expiry date cannot be earlier than manufacture date.")

    batch = ItemBatch.objects.create(
        organization_id=item.organization_id,
        item=item,
        batch_number=batch_num,
        manufacture_date=data.manufacture_date,
        expiry_date=data.expiry_date,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=item.organization_id,
        action="inventory.batch.created",
        target_type="inventory.ItemBatch",
        target_id=batch.id,
        correlation_id=data.context.correlation_id,
        metadata={"item_code": item.item_code, "batch_number": batch.batch_number},
    )

    return CreateItemBatchResult(
        batch_id=batch.id,
        item_id=item.id,
        batch_number=batch.batch_number,
        expiry_date=batch.expiry_date,
    )
