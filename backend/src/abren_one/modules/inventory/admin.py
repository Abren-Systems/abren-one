from django.contrib import admin

from abren_one.modules.inventory.models import (
    Item,
    ItemBatch,
    ItemCategory,
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
