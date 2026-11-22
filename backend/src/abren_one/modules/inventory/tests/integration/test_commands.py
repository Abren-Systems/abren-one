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
from abren_one.modules.inventory.application.commands.update_item import (
    UpdateItemInput,
)
from abren_one.modules.inventory.application.commands.update_item import (
    execute as update_item,
)
from abren_one.modules.inventory.application.commands.update_warehouse import (
    UpdateWarehouseInput,
)
from abren_one.modules.inventory.application.commands.update_warehouse import (
    execute as update_warehouse,
)
from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    OrganizationMismatchError,
)
from abren_one.modules.inventory.domain.value_objects import (
    ItemType,
    WarehouseType,
)
from abren_one.modules.inventory.models import (
    Item,
    ItemBatch,
    ItemCategory,
    StorageLocation,
    Warehouse,
)
from abren_one.modules.organizations.public import (
    CreateBranchInput,
    CreateOrganizationInput,
    create_branch,
    create_organization,
)
from abren_one.platform.audit.models import AuditEvent
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
            name=f"Relief Inventory NGO {uuid.uuid4().hex[:6]}",
            slug=f"relief-inv-{uuid.uuid4().hex[:6]}",
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
class TestItemCategoryCommands:
    def test_create_category_success(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        res = create_item_category(
            CreateItemCategoryInput(
                context=ctx,
                name="Medical Supplies",
                code="MED",
                description="Medicines and clinical tools",
            )
        )
        assert res.name == "Medical Supplies"
        assert res.code == "MED"
        assert res.parent_id is None

        cat = ItemCategory.objects.get(id=res.category_id)
        assert cat.organization_id == org_id

        # Subcategory
        sub_res = create_item_category(
            CreateItemCategoryInput(
                context=ctx,
                name="Vaccines & Cold Chain",
                code="MED-VAC",
                parent_id=res.category_id,
            )
        )
        assert sub_res.parent_id == res.category_id

        # Audit event recorded
        audit = AuditEvent.objects.filter(
            organization_id=org_id,
            action="inventory.category.created",
            target_id=res.category_id,
        ).first()
        assert audit is not None

    def test_duplicate_category_code_fails(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        create_item_category(CreateItemCategoryInput(context=ctx, name="Food", code="FOOD"))
        with pytest.raises(InventoryError, match="already exists"):
            create_item_category(CreateItemCategoryInput(context=ctx, name="Food 2", code="FOOD"))


@pytest.mark.django_db
class TestItemCommands:
    def test_create_and_update_item(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        cat = create_item_category(CreateItemCategoryInput(context=ctx, name="Nutrition", code="NUT"))

        res = create_item(
            CreateItemInput(
                context=ctx,
                category_id=cat.category_id,
                item_code="NUT-PLUMPY-01",
                name="Plumpy'Nut Therapeutic Food",
                description="Ready-to-use therapeutic food",
                unit_of_measure="boxes",
                item_type=ItemType.CONSUMABLE.value,
                track_batches=True,
                track_expiry=True,
                reorder_threshold=Decimal("50.00"),
                default_unit_cost=Decimal("45.00"),
            )
        )
        assert res.item_code == "NUT-PLUMPY-01"
        assert res.name == "Plumpy'Nut Therapeutic Food"
        assert res.is_active is True

        item = Item.objects.get(id=res.item_id)
        assert item.organization_id == org_id
        assert item.track_batches is True
        assert item.track_expiry is True

        # Update item
        up_res = update_item(
            UpdateItemInput(
                context=ctx,
                item_id=res.item_id,
                name="Plumpy'Nut 150-sachet Box",
                reorder_threshold=Decimal("100.00"),
            )
        )
        assert up_res.name == "Plumpy'Nut 150-sachet Box"
        item.refresh_from_db()
        assert item.name == "Plumpy'Nut 150-sachet Box"
        assert item.reorder_threshold == Decimal("100.00")

    def test_duplicate_item_code_fails(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        cat = create_item_category(CreateItemCategoryInput(context=ctx, name="Stationery", code="STAT"))
        create_item(
            CreateItemInput(
                context=ctx,
                category_id=cat.category_id,
                item_code="STAT-NOTE-01",
                name="Notebooks",
            )
        )
        with pytest.raises(InventoryError, match="already exists"):
            create_item(
                CreateItemInput(
                    context=ctx,
                    category_id=cat.category_id,
                    item_code="STAT-NOTE-01",
                    name="Duplicate Notebooks",
                )
            )

    def test_create_item_with_foreign_org_category_fails(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        _, ctx = org_context

        # Create Org B category
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org_b = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Org B",
                slug=f"org-b-{uuid.uuid4().hex[:6]}",
            )
        )
        ctx_b = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_b.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="admin",
        )
        cat_b = create_item_category(CreateItemCategoryInput(context=ctx_b, name="Org B Cat", code="CATB"))

        with pytest.raises(OrganizationMismatchError):
            create_item(
                CreateItemInput(
                    context=ctx,
                    category_id=cat_b.category_id,
                    item_code="ITEM-A",
                    name="Item in Org A",
                )
            )


@pytest.mark.django_db
class TestWarehouseCommands:
    def test_create_and_update_warehouse(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        branch = create_branch(
            CreateBranchInput(
                context=ctx,
                name="Addis Ababa Regional Office",
                code="ADD-REG",
            )
        )

        res = create_warehouse(
            CreateWarehouseInput(
                context=ctx,
                name="Addis Central Logistics Hub",
                code="WH-ADD-01",
                warehouse_type=WarehouseType.CENTRAL.value,
                branch_id=branch.branch_id,
                address="Bole Subcity, Addis Ababa",
            )
        )
        assert res.name == "Addis Central Logistics Hub"
        assert res.code == "WH-ADD-01"
        assert res.warehouse_type == WarehouseType.CENTRAL.value

        wh = Warehouse.objects.get(id=res.warehouse_id)
        assert wh.organization_id == org_id
        assert wh.branch_id == branch.branch_id

        # Update warehouse
        up_res = update_warehouse(
            UpdateWarehouseInput(
                context=ctx,
                warehouse_id=res.warehouse_id,
                name="Addis Central Logistics Hub (Expanded)",
            )
        )
        assert up_res.name == "Addis Central Logistics Hub (Expanded)"

    def test_warehouse_with_invalid_branch_fails(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        with pytest.raises(InventoryError, match="Referenced branch does not belong"):
            create_warehouse(
                CreateWarehouseInput(
                    context=ctx,
                    name="Invalid Warehouse",
                    code="WH-INV",
                    branch_id=uuid.uuid4(),
                )
            )

    def test_create_storage_location(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        wh_res = create_warehouse(CreateWarehouseInput(context=ctx, name="Main Depot", code="WH-MAIN"))

        loc_res = create_storage_location(
            CreateStorageLocationInput(
                context=ctx,
                warehouse_id=wh_res.warehouse_id,
                name="Cold Room 1",
                code="COLD-01",
            )
        )
        assert loc_res.name == "Cold Room 1"
        assert loc_res.code == "COLD-01"

        loc = StorageLocation.objects.get(id=loc_res.location_id)
        assert loc.warehouse_id == wh_res.warehouse_id

        # Duplicate location code within the same warehouse fails
        with pytest.raises(InventoryError, match="already exists"):
            create_storage_location(
                CreateStorageLocationInput(
                    context=ctx,
                    warehouse_id=wh_res.warehouse_id,
                    name="Cold Room Duplicate",
                    code="COLD-01",
                )
            )


@pytest.mark.django_db
class TestItemBatchCommands:
    def test_create_batch(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        cat = create_item_category(CreateItemCategoryInput(context=ctx, name="Medicine", code="MED-DRUG"))
        item_res = create_item(
            CreateItemInput(
                context=ctx,
                category_id=cat.category_id,
                item_code="AMOX-500",
                name="Amoxicillin 500mg",
                track_batches=True,
                track_expiry=True,
            )
        )

        today = date.today()
        exp = today + timedelta(days=365)
        batch_res = create_item_batch(
            CreateItemBatchInput(
                context=ctx,
                item_id=item_res.item_id,
                batch_number="LOT-2026-X1",
                manufacture_date=today,
                expiry_date=exp,
            )
        )
        assert batch_res.batch_number == "LOT-2026-X1"
        assert batch_res.expiry_date == exp

        batch = ItemBatch.objects.get(id=batch_res.batch_id)
        assert batch.organization_id == org_id
        assert batch.item_id == item_res.item_id

        # Duplicate batch number for same item fails
        with pytest.raises(InventoryError, match="already exists"):
            create_item_batch(
                CreateItemBatchInput(
                    context=ctx,
                    item_id=item_res.item_id,
                    batch_number="LOT-2026-X1",
                )
            )

        # Expiry date before manufacture date fails
        with pytest.raises(InventoryError, match="expiry date cannot be earlier"):
            create_item_batch(
                CreateItemBatchInput(
                    context=ctx,
                    item_id=item_res.item_id,
                    batch_number="LOT-INVALID-DATE",
                    manufacture_date=today,
                    expiry_date=today - timedelta(days=1),
                )
            )
