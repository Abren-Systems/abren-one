from django.urls import path

from abren_one.modules.inventory.interfaces.api.v1.views import (
    ItemBatchCreateView,
    ItemCategoryListCreateView,
    ItemDetailUpdateView,
    ItemListCreateView,
    StorageLocationCreateView,
    WarehouseDetailUpdateView,
    WarehouseListCreateView,
)

app_name = "inventory"

urlpatterns = [
    # Item Categories
    path("categories/", ItemCategoryListCreateView.as_view(), name="category-list-create"),
    # Items
    path("items/", ItemListCreateView.as_view(), name="item-list-create"),
    path("items/<uuid:item_id>/", ItemDetailUpdateView.as_view(), name="item-detail"),
    path("items/<uuid:item_id>/batches/", ItemBatchCreateView.as_view(), name="item-batch-create"),
    # Warehouses
    path("warehouses/", WarehouseListCreateView.as_view(), name="warehouse-list-create"),
    path("warehouses/<uuid:warehouse_id>/", WarehouseDetailUpdateView.as_view(), name="warehouse-detail"),
    path(
        "warehouses/<uuid:warehouse_id>/locations/",
        StorageLocationCreateView.as_view(),
        name="storage-location-create",
    ),
]
