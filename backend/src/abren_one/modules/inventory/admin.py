from django.contrib import admin

from abren_one.modules.inventory.models import (
    Item,
    ItemBatch,
    ItemCategory,
    StockBalance,
    StockLedgerEntry,
    StockTransaction,
    StorageLocation,
    Warehouse,
)


class ItemBatchInline(admin.TabularInline):
    model = ItemBatch
    extra = 0
    readonly_fields = ["created_at"]


class StorageLocationInline(admin.TabularInline):
    model = StorageLocation
    extra = 0
    readonly_fields = ["created_at"]


class StockLedgerEntryInline(admin.TabularInline):
    model = StockLedgerEntry
    extra = 0
    readonly_fields = [
        "item",
        "batch",
        "warehouse",
        "location",
        "quantity",
        "unit_cost",
        "program_id",
        "activity_id",
        "created_at",
    ]
    can_delete = False


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "organization", "parent"]
    search_fields = ["name", "code"]
    list_filter = ["organization"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "item_code",
        "name",
        "category",
        "unit_of_measure",
        "item_type",
        "reorder_threshold",
        "is_active",
        "organization",
    ]
    search_fields = ["item_code", "name"]
    list_filter = ["item_type", "is_active", "organization"]
    inlines = [ItemBatchInline]


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "warehouse_type", "is_active", "organization"]
    search_fields = ["name", "code"]
    list_filter = ["warehouse_type", "is_active", "organization"]
    inlines = [StorageLocationInline]


@admin.register(ItemBatch)
class ItemBatchAdmin(admin.ModelAdmin):
    list_display = ["item", "batch_number", "manufacture_date", "expiry_date", "organization"]
    search_fields = ["batch_number", "item__name", "item__item_code"]
    list_filter = ["organization"]


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ["warehouse", "name", "code", "is_active"]
    search_fields = ["name", "code", "warehouse__name"]


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_number",
        "transaction_type",
        "status",
        "source_warehouse",
        "destination_warehouse",
        "transaction_date",
        "organization",
    ]
    search_fields = ["transaction_number", "reference_document", "donor_name"]
    list_filter = ["transaction_type", "status", "organization"]
    inlines = [StockLedgerEntryInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(StockLedgerEntry)
class StockLedgerEntryAdmin(admin.ModelAdmin):
    list_display = [
        "transaction",
        "item",
        "batch",
        "warehouse",
        "quantity",
        "unit_cost",
        "created_at",
    ]
    search_fields = ["item__name", "item__item_code", "transaction__transaction_number"]
    list_filter = ["warehouse", "organization"]
    readonly_fields = [
        "transaction",
        "item",
        "batch",
        "warehouse",
        "location",
        "quantity",
        "unit_cost",
        "program_id",
        "activity_id",
        "created_at",
    ]


@admin.register(StockBalance)
class StockBalanceAdmin(admin.ModelAdmin):
    list_display = [
        "item",
        "warehouse",
        "location",
        "batch",
        "quantity_on_hand",
        "quantity_reserved",
        "organization",
    ]
    search_fields = ["item__name", "item__item_code", "warehouse__name", "warehouse__code"]
    list_filter = ["warehouse", "organization"]
