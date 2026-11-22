import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from abren_one.modules.inventory.application.commands.create_item import (
    CreateItemInput,
)
from abren_one.modules.inventory.application.commands.create_item import (
    execute as create_item,
)
from abren_one.modules.inventory.application.commands.create_item_batch import (
    CreateItemBatchInput,
)
from abren_one.modules.inventory.application.commands.create_item_batch import (
    execute as create_item_batch,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    CreateItemCategoryInput,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    execute as create_item_category,
)
from abren_one.modules.inventory.application.commands.create_storage_location import (
    CreateStorageLocationInput,
)
from abren_one.modules.inventory.application.commands.create_storage_location import (
    execute as create_storage_location,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    CreateWarehouseInput,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    execute as create_warehouse,
)
from abren_one.modules.inventory.application.queries.get_item import (
    execute as get_item,
)
from abren_one.modules.inventory.application.queries.get_warehouse import (
    execute as get_warehouse,
)
from abren_one.modules.inventory.application.queries.list_item_categories import (
    execute as list_item_categories,
)
from abren_one.modules.inventory.application.queries.list_items import (
    execute as list_items,
)
from abren_one.modules.inventory.application.queries.list_warehouses import (
    execute as list_warehouses,
)
from abren_one.modules.inventory.domain.value_objects import (
    ItemType,
    WarehouseType,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.fixture
def org_context() -> tuple[uuid.UUID, ExecutionContext]:
    actor_id = uuid.uuid4()
    corr_id = uuid.uuid4()
    init_ctx = ExecutionContext(
        actor_type=ActorType.SYSTEM,
        actor_id=None,
        organization_id=None,
        correlation_id=corr_id,
    )
    org_res = create_organization(
        CreateOrganizationInput(
            context=init_ctx,
            name=f"Inventory Query Org {uuid.uuid4().hex[:6]}",
            slug=f"inv-q-org-{uuid.uuid4().hex[:6]}",
        )
    )
    ctx = ExecutionContext(
        actor_type=ActorType.USER,
        actor_id=actor_id,
        organization_id=org_res.organization_id,
        correlation_id=corr_id,
        actor_role="admin",
    )
    return org_res.organization_id, ctx


@pytest.mark.django_db
class TestMasterDataQueries:
    def test_list_and_get_categories(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        parent = create_item_category(CreateItemCategoryInput(context=ctx, name="Logistics", code="LOG"))
        create_item_category(
            CreateItemCategoryInput(context=ctx, name="Fleet Parts", code="LOG-FLT", parent_id=parent.category_id)
        )

        cats = list_item_categories(ctx)
        assert len(cats) == 2
        fleet = next(c for c in cats if c.code == "LOG-FLT")
        assert fleet.parent_name == "Logistics"

    def test_list_and_get_items(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        cat1 = create_item_category(CreateItemCategoryInput(context=ctx, name="Food", code="FOOD"))
        cat2 = create_item_category(CreateItemCategoryInput(context=ctx, name="Shelter", code="SHEL"))

        item1 = create_item(
            CreateItemInput(
                context=ctx,
                category_id=cat1.category_id,
                item_code="FOOD-WHEAT",
                name="Wheat Flour 50kg",
                item_type=ItemType.CONSUMABLE.value,
                track_batches=True,
                reorder_threshold=Decimal("20.00"),
            )
        )
        create_item(
            CreateItemInput(
                context=ctx,
                category_id=cat2.category_id,
                item_code="SHEL-TENT-01",
                name="Family Relief Tent",
                item_type=ItemType.RELIEF_GOOD.value,
            )
        )

        # Filter by category
        food_items = list_items(ctx, category_id=cat1.category_id)
        assert len(food_items) == 1
        assert food_items[0].item_code == "FOOD-WHEAT"

        # Filter by search
        search_items = list_items(ctx, search="Tent")
        assert len(search_items) == 1
        assert search_items[0].item_code == "SHEL-TENT-01"

        # Add batch to item1 and get item detail
        exp = date.today() + timedelta(days=180)
        create_item_batch(
            CreateItemBatchInput(
                context=ctx,
                item_id=item1.item_id,
                batch_number="BATCH-WHEAT-2026",
                expiry_date=exp,
            )
        )

        detail = get_item(ctx, item1.item_id)
        assert detail.item_code == "FOOD-WHEAT"
        assert detail.category_name == "Food"
        assert len(detail.batches) == 1
        assert detail.batches[0].batch_number == "BATCH-WHEAT-2026"
        assert detail.batches[0].expiry_date == exp

    def test_list_and_get_warehouses(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        wh1 = create_warehouse(
            CreateWarehouseInput(
                context=ctx,
                name="Hawassa Depot",
                code="WH-HAW",
                warehouse_type=WarehouseType.REGIONAL_DEPOT.value,
            )
        )
        create_warehouse(
            CreateWarehouseInput(
                context=ctx,
                name="Dilla Dispensary",
                code="WH-DIL",
                warehouse_type=WarehouseType.FIELD_DISPENSARY.value,
            )
        )

        # Add storage locations to wh1
        create_storage_location(
            CreateStorageLocationInput(
                context=ctx,
                warehouse_id=wh1.warehouse_id,
                name="Rack 1",
                code="R1",
            )
        )
        create_storage_location(
            CreateStorageLocationInput(
                context=ctx,
                warehouse_id=wh1.warehouse_id,
                name="Rack 2",
                code="R2",
            )
        )

        all_wh = list_warehouses(ctx)
        assert len(all_wh) == 2

        dispensaries = list_warehouses(ctx, warehouse_type=WarehouseType.FIELD_DISPENSARY.value)
        assert len(dispensaries) == 1
        assert dispensaries[0].code == "WH-DIL"

        haw_summary = next(w for w in all_wh if w.code == "WH-HAW")
        assert haw_summary.location_count == 2

        # Detailed view
        detail = get_warehouse(ctx, wh1.warehouse_id)
        assert detail.code == "WH-HAW"
        assert len(detail.locations) == 2
        assert {loc.code for loc in detail.locations} == {"R1", "R2"}
