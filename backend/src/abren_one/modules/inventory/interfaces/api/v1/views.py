import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

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
from abren_one.modules.inventory.interfaces.api.v1.serializers import (
    CreateItemBatchRequestSerializer,
    CreateItemCategoryRequestSerializer,
    CreateItemRequestSerializer,
    CreateStorageLocationRequestSerializer,
    CreateWarehouseRequestSerializer,
    ItemCategoryResponseSerializer,
    ItemDetailResponseSerializer,
    ItemSummaryResponseSerializer,
    UpdateItemRequestSerializer,
    UpdateWarehouseRequestSerializer,
    WarehouseDetailResponseSerializer,
    WarehouseSummaryResponseSerializer,
)
from abren_one.platform.authorization.permissions import require_permission
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class ItemCategoryListCreateView(APIView):
    """List and create item categories."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("inventory:items:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("inventory:items:view")(),
        ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        categories = list_item_categories(ctx)
        serializer = ItemCategoryResponseSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateItemCategoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = create_item_category(
            CreateItemCategoryInput(
                context=ctx,
                name=validated["name"],
                code=validated["code"],
                description=validated.get("description", ""),
                parent_id=validated.get("parent_id"),
            )
        )
        return Response(
            {
                "category_id": result.category_id,
                "name": result.name,
                "code": result.code,
                "parent_id": result.parent_id,
            },
            status=status.HTTP_201_CREATED,
        )


class ItemListCreateView(APIView):
    """List and create stock-tracked items."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("inventory:items:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("inventory:items:view")(),
        ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        cat_param = request.query_params.get("category_id")
        category_id = uuid.UUID(cat_param) if cat_param else None
        item_type = request.query_params.get("item_type")
        is_active_param = request.query_params.get("is_active")
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() in ("true", "1")
        search = request.query_params.get("search")

        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        items = list_items(
            context=ctx,
            category_id=category_id,
            item_type=item_type,
            is_active=is_active,
            search=search,
            limit=limit,
            offset=offset,
        )
        serializer = ItemSummaryResponseSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateItemRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = create_item(
            CreateItemInput(
                context=ctx,
                category_id=validated["category_id"],
                item_code=validated["item_code"],
                name=validated["name"],
                description=validated.get("description", ""),
                unit_of_measure=validated.get("unit_of_measure", "each"),
                item_type=validated.get("item_type", "consumable"),
                track_batches=validated.get("track_batches", False),
                track_expiry=validated.get("track_expiry", False),
                reorder_threshold=validated.get("reorder_threshold", 0),
                default_unit_cost=validated.get("default_unit_cost", 0),
            )
        )
        return Response(
            {
                "item_id": result.item_id,
                "item_code": result.item_code,
                "name": result.name,
                "unit_of_measure": result.unit_of_measure,
                "item_type": result.item_type,
                "is_active": result.is_active,
            },
            status=status.HTTP_201_CREATED,
        )


class ItemDetailUpdateView(APIView):
    """Retrieve and update an individual inventory item."""

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("inventory:items:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("inventory:items:view")(),
        ]

    def get(self, request: Request, item_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        item = get_item(ctx, item_id)
        serializer = ItemDetailResponseSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, item_id: uuid.UUID) -> Response:
        serializer = UpdateItemRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = update_item(
            UpdateItemInput(
                context=ctx,
                item_id=item_id,
                name=validated.get("name"),
                description=validated.get("description"),
                category_id=validated.get("category_id"),
                unit_of_measure=validated.get("unit_of_measure"),
                item_type=validated.get("item_type"),
                track_batches=validated.get("track_batches"),
                track_expiry=validated.get("track_expiry"),
                reorder_threshold=validated.get("reorder_threshold"),
                default_unit_cost=validated.get("default_unit_cost"),
                is_active=validated.get("is_active"),
            )
        )
        return Response(
            {
                "item_id": result.item_id,
                "item_code": result.item_code,
                "name": result.name,
                "is_active": result.is_active,
            },
            status=status.HTTP_200_OK,
        )


class ItemBatchCreateView(APIView):
    """Register a new batch for an item."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:items:manage"),
    ]

    def post(self, request: Request, item_id: uuid.UUID) -> Response:
        serializer = CreateItemBatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = create_item_batch(
            CreateItemBatchInput(
                context=ctx,
                item_id=item_id,
                batch_number=validated["batch_number"],
                manufacture_date=validated.get("manufacture_date"),
                expiry_date=validated.get("expiry_date"),
            )
        )
        return Response(
            {
                "batch_id": result.batch_id,
                "item_id": result.item_id,
                "batch_number": result.batch_number,
                "expiry_date": result.expiry_date,
            },
            status=status.HTTP_201_CREATED,
        )


class WarehouseListCreateView(APIView):
    """List and create warehouse facilities."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("inventory:warehouses:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("inventory:warehouses:view")(),
        ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        wh_type = request.query_params.get("warehouse_type")
        is_active_param = request.query_params.get("is_active")
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() in ("true", "1")

        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        warehouses = list_warehouses(
            context=ctx,
            warehouse_type=wh_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        serializer = WarehouseSummaryResponseSerializer(warehouses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateWarehouseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = create_warehouse(
            CreateWarehouseInput(
                context=ctx,
                name=validated["name"],
                code=validated["code"],
                warehouse_type=validated.get("warehouse_type", "regional_depot"),
                branch_id=validated.get("branch_id"),
                custodian_id=validated.get("custodian_id"),
                address=validated.get("address", ""),
            )
        )
        return Response(
            {
                "warehouse_id": result.warehouse_id,
                "name": result.name,
                "code": result.code,
                "warehouse_type": result.warehouse_type,
                "is_active": result.is_active,
            },
            status=status.HTTP_201_CREATED,
        )


class WarehouseDetailUpdateView(APIView):
    """Retrieve and update an individual warehouse facility."""

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("inventory:warehouses:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("inventory:warehouses:view")(),
        ]

    def get(self, request: Request, warehouse_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        warehouse = get_warehouse(ctx, warehouse_id)
        serializer = WarehouseDetailResponseSerializer(warehouse)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, warehouse_id: uuid.UUID) -> Response:
        serializer = UpdateWarehouseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = update_warehouse(
            UpdateWarehouseInput(
                context=ctx,
                warehouse_id=warehouse_id,
                name=validated.get("name"),
                warehouse_type=validated.get("warehouse_type"),
                branch_id=validated.get("branch_id"),
                custodian_id=validated.get("custodian_id"),
                address=validated.get("address"),
                is_active=validated.get("is_active"),
            )
        )
        return Response(
            {
                "warehouse_id": result.warehouse_id,
                "name": result.name,
                "code": result.code,
                "is_active": result.is_active,
            },
            status=status.HTTP_200_OK,
        )


class StorageLocationCreateView(APIView):
    """Create a storage location/bin inside a warehouse."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:warehouses:manage"),
    ]

    def post(self, request: Request, warehouse_id: uuid.UUID) -> Response:
        serializer = CreateStorageLocationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = create_storage_location(
            CreateStorageLocationInput(
                context=ctx,
                warehouse_id=warehouse_id,
                name=validated["name"],
                code=validated["code"],
            )
        )
        return Response(
            {
                "location_id": result.location_id,
                "warehouse_id": result.warehouse_id,
                "name": result.name,
                "code": result.code,
                "is_active": result.is_active,
            },
            status=status.HTTP_201_CREATED,
        )
