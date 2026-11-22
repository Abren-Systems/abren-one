from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import ItemCategory
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ItemCategorySummaryResult:
    id: UUID
    name: str
    code: str
    description: str
    parent_id: UUID | None
    parent_name: str | None


def execute(context: ExecutionContext) -> list[ItemCategorySummaryResult]:
    """List all item categories for the active organization."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    categories = (
        ItemCategory.objects.filter(organization_id=context.organization_id).select_related("parent").order_by("name")
    )

    return [
        ItemCategorySummaryResult(
            id=cat.id,
            name=cat.name,
            code=cat.code,
            description=cat.description,
            parent_id=cat.parent_id,
            parent_name=cat.parent.name if cat.parent else None,
        )
        for cat in categories
    ]
