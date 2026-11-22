import contextlib
import datetime
import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.modules.inventory.application.commands.adjust_stock import (
    AdjustmentLineInput,
    AdjustStockInput,
)
from abren_one.modules.inventory.application.commands.adjust_stock import (
    execute as adjust_stock,
)
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
from abren_one.modules.inventory.application.commands.issue_stock import (
    IssueLineInput,
    IssueStockInput,
)
from abren_one.modules.inventory.application.commands.issue_stock import (
    execute as issue_stock,
)
from abren_one.modules.inventory.application.commands.receive_in_kind_donation import (
    DonationReceiptLineInput,
    ReceiveDonationInput,
)
from abren_one.modules.inventory.application.commands.receive_in_kind_donation import (
    execute as receive_in_kind_donation,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    OpeningStockLineInput,
    ReceiveOpeningStockInput,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    execute as receive_opening_stock,
)
from abren_one.modules.inventory.application.commands.transfer_stock import (
    TransferLineInput,
    TransferStockInput,
)
from abren_one.modules.inventory.application.commands.transfer_stock import (
    execute as transfer_stock,
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
from abren_one.modules.inventory.application.commands.write_off_stock import (
    WriteOffLineInput,
    WriteOffStockInput,
)
from abren_one.modules.inventory.application.commands.write_off_stock import (
    execute as write_off_stock,
)
from abren_one.modules.inventory.application.queries.get_expiring_batches import (
    execute as get_expiring_batches,
)
from abren_one.modules.inventory.application.queries.get_item import (
    execute as get_item,
)
from abren_one.modules.inventory.application.queries.get_reorder_alerts import (
    execute as get_reorder_alerts,
)
from abren_one.modules.inventory.application.queries.get_stock_balances import (
    execute as get_stock_balances,
)
from abren_one.modules.inventory.application.queries.get_stock_ledger import (
    execute as get_stock_ledger,
)
from abren_one.modules.inventory.application.queries.get_transaction_detail import (
    execute as get_transaction_detail,
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
from abren_one.modules.inventory.application.queries.reconcile_balances import (
    execute as reconcile_balances,
)
from abren_one.modules.inventory.interfaces.api.v1.serializers import (
    AdjustStockRequestSerializer,
    CreateItemBatchRequestSerializer,
    CreateItemCategoryRequestSerializer,
    CreateItemRequestSerializer,
    CreateStorageLocationRequestSerializer,
    CreateWarehouseRequestSerializer,
    ExpiringBatchResponseSerializer,
    IssueStockRequestSerializer,
    ItemCategoryResponseSerializer,
    ItemDetailResponseSerializer,
    ItemSummaryResponseSerializer,
    ReceiveDonationRequestSerializer,
    ReceiveOpeningStockRequestSerializer,
    ReorderAlertResponseSerializer,
    StockBalanceResponseSerializer,
    StockLedgerResponseSerializer,
    TransactionDetailResponseSerializer,
    TransferStockRequestSerializer,
    UpdateItemRequestSerializer,
    UpdateWarehouseRequestSerializer,
    WarehouseDetailResponseSerializer,
    WarehouseSummaryResponseSerializer,
    WriteOffStockRequestSerializer,
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
    """List and create stock items."""

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
        category_id = None
        if request.query_params.get("category_id"):
            with contextlib.suppress(ValueError):
                category_id = uuid.UUID(request.query_params["category_id"])

        is_active = None
        if "is_active" in request.query_params:
            is_active = request.query_params["is_active"].lower() in ("true", "1")

        search = request.query_params.get("search")

        try:
            limit = min(max(1, int(request.query_params.get("limit", 50))), 200)
        except ValueError, TypeError:
            limit = 50

        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        items = list_items(
            context=ctx,
            category_id=category_id,
            search=search,
            is_active=is_active,
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
            },
            status=status.HTTP_201_CREATED,
        )


class ItemDetailView(APIView):
    """Retrieve and update an individual stock item."""

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
                "name": result.name,
                "is_active": result.is_active,
            },
            status=status.HTTP_200_OK,
        )


class ItemBatchCreateView(APIView):
    """Create a new batch/lot for an item."""

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
    """List and create warehouses."""

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
        is_active = None
        if "is_active" in request.query_params:
            is_active = request.query_params["is_active"].lower() in ("true", "1")

        branch_id = None
        if request.query_params.get("branch_id"):
            with contextlib.suppress(ValueError):
                branch_id = uuid.UUID(request.query_params["branch_id"])

        try:
            limit = min(max(1, int(request.query_params.get("limit", 50))), 200)
        except ValueError, TypeError:
            limit = 50

        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        warehouses = list_warehouses(
            context=ctx,
            branch_id=branch_id,
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
            },
            status=status.HTTP_201_CREATED,
        )


class WarehouseDetailView(APIView):
    """Retrieve and update a warehouse."""

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
        wh = get_warehouse(ctx, warehouse_id)
        serializer = WarehouseDetailResponseSerializer(wh)
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


# ── Stock Operations & Queries Views ──────────────────────────────────────────


class StockBalanceListView(APIView):
    """List operational stock balances."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:view"),
    ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        warehouse_id = None
        if request.query_params.get("warehouse_id"):
            with contextlib.suppress(ValueError):
                warehouse_id = uuid.UUID(request.query_params["warehouse_id"])

        item_id = None
        if request.query_params.get("item_id"):
            with contextlib.suppress(ValueError):
                item_id = uuid.UUID(request.query_params["item_id"])

        low_stock_only = request.query_params.get("low_stock_only", "").lower() in ("true", "1")

        try:
            limit = min(max(1, int(request.query_params.get("limit", 50))), 200)
        except ValueError, TypeError:
            limit = 50

        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        balances = get_stock_balances(
            context=ctx,
            warehouse_id=warehouse_id,
            item_id=item_id,
            low_stock_only=low_stock_only,
            limit=limit,
            offset=offset,
        )
        serializer = StockBalanceResponseSerializer(balances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StockLedgerListView(APIView):
    """Retrieve immutable chronological stock movements."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:view"),
    ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        warehouse_id = None
        if request.query_params.get("warehouse_id"):
            with contextlib.suppress(ValueError):
                warehouse_id = uuid.UUID(request.query_params["warehouse_id"])

        item_id = None
        if request.query_params.get("item_id"):
            with contextlib.suppress(ValueError):
                item_id = uuid.UUID(request.query_params["item_id"])

        transaction_id = None
        if request.query_params.get("transaction_id"):
            with contextlib.suppress(ValueError):
                transaction_id = uuid.UUID(request.query_params["transaction_id"])

        from_date = None
        if request.query_params.get("from_date"):
            with contextlib.suppress(ValueError):
                from_date = datetime.date.fromisoformat(request.query_params["from_date"])

        to_date = None
        if request.query_params.get("to_date"):
            with contextlib.suppress(ValueError):
                to_date = datetime.date.fromisoformat(request.query_params["to_date"])

        try:
            limit = min(max(1, int(request.query_params.get("limit", 50))), 200)
        except ValueError, TypeError:
            limit = 50

        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        entries = get_stock_ledger(
            context=ctx,
            warehouse_id=warehouse_id,
            item_id=item_id,
            transaction_id=transaction_id,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )
        serializer = StockLedgerResponseSerializer(entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StockTransactionDetailView(APIView):
    """Retrieve full details of a stock transaction."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:view"),
    ]

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        detail = get_transaction_detail(ctx, pk)
        serializer = TransactionDetailResponseSerializer(detail)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceiveOpeningStockView(APIView):
    """Record baseline opening stock inventory into a warehouse."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:receive"),
    ]

    def post(self, request: Request) -> Response:
        serializer = ReceiveOpeningStockRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        val = serializer.validated_data

        ctx = build_execution_context(request)
        lines = [
            OpeningStockLineInput(
                item_id=line["item_id"],
                quantity=line["quantity"],
                unit_cost=line.get("unit_cost", 0),
                location_id=line.get("location_id"),
                batch_id=line.get("batch_id"),
            )
            for line in val["lines"]
        ]

        result = receive_opening_stock(
            ReceiveOpeningStockInput(
                context=ctx,
                warehouse_id=val["warehouse_id"],
                transaction_date=val["transaction_date"],
                reference_document=val.get("reference_document", ""),
                notes=val.get("notes", ""),
                lines=lines,
            )
        )
        return Response(
            {
                "transaction_id": result.transaction_id,
                "transaction_number": result.transaction_number,
                "total_lines": result.total_lines,
                "total_quantity": result.total_quantity,
            },
            status=status.HTTP_201_CREATED,
        )


class ReceiveDonationView(APIView):
    """Record in-kind donation stock receipt."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:receive"),
    ]

    def post(self, request: Request) -> Response:
        serializer = ReceiveDonationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        val = serializer.validated_data

        ctx = build_execution_context(request)
        lines = [
            DonationReceiptLineInput(
                item_id=line["item_id"],
                quantity=line["quantity"],
                unit_cost=line.get("unit_cost", 0),
                location_id=line.get("location_id"),
                batch_id=line.get("batch_id"),
            )
            for line in val["lines"]
        ]

        result = receive_in_kind_donation(
            ReceiveDonationInput(
                context=ctx,
                warehouse_id=val["warehouse_id"],
                donor_name=val["donor_name"],
                transaction_date=val["transaction_date"],
                reference_document=val.get("reference_document", ""),
                notes=val.get("notes", ""),
                lines=lines,
            )
        )
        return Response(
            {
                "transaction_id": result.transaction_id,
                "transaction_number": result.transaction_number,
                "donor_name": result.donor_name,
                "total_lines": result.total_lines,
                "total_quantity": result.total_quantity,
            },
            status=status.HTTP_201_CREATED,
        )


class TransferStockView(APIView):
    """Execute immediate inter-warehouse stock transfer."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:transfer"),
    ]

    def post(self, request: Request) -> Response:
        serializer = TransferStockRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        val = serializer.validated_data

        ctx = build_execution_context(request)
        lines = [
            TransferLineInput(
                item_id=line["item_id"],
                quantity=line["quantity"],
                source_location_id=line.get("source_location_id"),
                destination_location_id=line.get("destination_location_id"),
                batch_id=line.get("batch_id"),
            )
            for line in val["lines"]
        ]

        result = transfer_stock(
            TransferStockInput(
                context=ctx,
                source_warehouse_id=val["source_warehouse_id"],
                destination_warehouse_id=val["destination_warehouse_id"],
                transaction_date=val["transaction_date"],
                reference_document=val.get("reference_document", ""),
                notes=val.get("notes", ""),
                lines=lines,
            )
        )
        return Response(
            {
                "transaction_id": result.transaction_id,
                "transaction_number": result.transaction_number,
                "total_lines": result.total_lines,
                "total_quantity_transferred": result.total_quantity_transferred,
            },
            status=status.HTTP_201_CREATED,
        )


class IssueStockView(APIView):
    """Issue inventory for general supplies or program delivery."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:issue"),
    ]

    def post(self, request: Request) -> Response:
        serializer = IssueStockRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        val = serializer.validated_data

        ctx = build_execution_context(request)
        lines = [
            IssueLineInput(
                item_id=line["item_id"],
                quantity=line["quantity"],
                location_id=line.get("location_id"),
                batch_id=line.get("batch_id"),
                program_id=line.get("program_id"),
                activity_id=line.get("activity_id"),
            )
            for line in val["lines"]
        ]

        result = issue_stock(
            IssueStockInput(
                context=ctx,
                warehouse_id=val["warehouse_id"],
                transaction_date=val["transaction_date"],
                is_program_issue=val.get("is_program_issue", False),
                recipient_name=val.get("recipient_name", ""),
                reference_document=val.get("reference_document", ""),
                notes=val.get("notes", ""),
                lines=lines,
            )
        )
        return Response(
            {
                "transaction_id": result.transaction_id,
                "transaction_number": result.transaction_number,
                "transaction_type": result.transaction_type,
                "total_lines": result.total_lines,
                "total_quantity_issued": result.total_quantity_issued,
            },
            status=status.HTTP_201_CREATED,
        )


class AdjustStockView(APIView):
    """Reconcile physical cycle count discrepancies (Owner/Admin only)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:adjust"),
    ]

    def post(self, request: Request) -> Response:
        serializer = AdjustStockRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        val = serializer.validated_data

        ctx = build_execution_context(request)
        lines = [
            AdjustmentLineInput(
                item_id=line["item_id"],
                actual_quantity_counted=line["actual_quantity_counted"],
                location_id=line.get("location_id"),
                batch_id=line.get("batch_id"),
                reason=line.get("reason", ""),
            )
            for line in val["lines"]
        ]

        result = adjust_stock(
            AdjustStockInput(
                context=ctx,
                warehouse_id=val["warehouse_id"],
                transaction_date=val["transaction_date"],
                justification=val["justification"],
                reference_document=val.get("reference_document", ""),
                lines=lines,
            )
        )
        return Response(
            {
                "transaction_id": result.transaction_id,
                "transaction_number": result.transaction_number,
                "lines_adjusted": result.lines_adjusted,
                "net_quantity_delta": result.net_quantity_delta,
            },
            status=status.HTTP_201_CREATED,
        )


class WriteOffStockView(APIView):
    """Authorize disposal/write-off of damaged or expired stock (Owner/Admin only)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:adjust"),
    ]

    def post(self, request: Request) -> Response:
        serializer = WriteOffStockRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        val = serializer.validated_data

        ctx = build_execution_context(request)
        lines = [
            WriteOffLineInput(
                item_id=line["item_id"],
                quantity=line["quantity"],
                reason=line["reason"],
                location_id=line.get("location_id"),
                batch_id=line.get("batch_id"),
            )
            for line in val["lines"]
        ]

        result = write_off_stock(
            WriteOffStockInput(
                context=ctx,
                warehouse_id=val["warehouse_id"],
                transaction_date=val["transaction_date"],
                approval_reference=val["approval_reference"],
                justification=val["justification"],
                lines=lines,
            )
        )
        return Response(
            {
                "transaction_id": result.transaction_id,
                "transaction_number": result.transaction_number,
                "approval_reference": result.approval_reference,
                "total_lines": result.total_lines,
                "total_quantity_written_off": result.total_quantity_written_off,
            },
            status=status.HTTP_201_CREATED,
        )


class StockAlertsView(APIView):
    """Retrieve operational stock alerts (low stock & expiring batches)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:view"),
    ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        warehouse_id = None
        if request.query_params.get("warehouse_id"):
            with contextlib.suppress(ValueError):
                warehouse_id = uuid.UUID(request.query_params["warehouse_id"])

        try:
            days_ahead = int(request.query_params.get("days_ahead", 90))
        except ValueError, TypeError:
            days_ahead = 90

        reorder_alerts = get_reorder_alerts(ctx, warehouse_id=warehouse_id)
        expiring_batches = get_expiring_batches(ctx, days_ahead=days_ahead, warehouse_id=warehouse_id)

        return Response(
            {
                "reorder_alerts": ReorderAlertResponseSerializer(reorder_alerts, many=True).data,
                "expiring_batches": ExpiringBatchResponseSerializer(expiring_batches, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class ReconciliationView(APIView):
    """Audit materialized stock balance projections against the immutable ledger."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("inventory:stock:view"),
    ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        warehouse_id = None
        if request.query_params.get("warehouse_id"):
            with contextlib.suppress(ValueError):
                warehouse_id = uuid.UUID(request.query_params["warehouse_id"])

        item_id = None
        if request.query_params.get("item_id"):
            with contextlib.suppress(ValueError):
                item_id = uuid.UUID(request.query_params["item_id"])

        report = reconcile_balances(ctx, warehouse_id=warehouse_id, item_id=item_id)
        return Response(
            {
                "total_balances_checked": report.total_balances_checked,
                "discrepancies_count": report.discrepancies_count,
                "is_healthy": report.is_healthy,
                "discrepancies": [
                    {
                        "warehouse_id": str(d.warehouse_id),
                        "warehouse_name": d.warehouse_name,
                        "item_id": str(d.item_id),
                        "item_name": d.item_name,
                        "location_id": str(d.location_id) if d.location_id else None,
                        "batch_id": str(d.batch_id) if d.batch_id else None,
                        "materialized_quantity": str(d.materialized_quantity),
                        "ledger_sum_quantity": str(d.ledger_sum_quantity),
                        "difference": str(d.difference),
                    }
                    for d in report.discrepancies
                ],
            },
            status=status.HTTP_200_OK,
        )
