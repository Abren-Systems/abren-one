from django.urls import path

from abren_one.modules.inventory.interfaces.api.v1.views import (
    AdjustStockView,
    IssueStockView,
    ItemBatchCreateView,
    ItemCategoryListCreateView,
    ItemDetailView,
    ItemListCreateView,
    PendingGRNsListView,
    ReceiveDonationView,
    ReceiveOpeningStockView,
    ReceivePurchasedStockView,
    ReconciliationView,
    StockAlertsView,
    StockBalanceListView,
    StockLedgerListView,
    StockTransactionDetailView,
    StorageLocationCreateView,
    TransferStockView,
    WarehouseDetailView,
    WarehouseListCreateView,
    WriteOffStockView,
)

app_name = "inventory"

urlpatterns = [
    # Item Categories
    path("categories/", ItemCategoryListCreateView.as_view(), name="category-list-create"),
    # Items
    path("items/", ItemListCreateView.as_view(), name="item-list-create"),
    path("items/<uuid:item_id>/", ItemDetailView.as_view(), name="item-detail"),
    path("items/<uuid:item_id>/batches/", ItemBatchCreateView.as_view(), name="item-batch-create"),
    # Warehouses & Locations
    path("warehouses/", WarehouseListCreateView.as_view(), name="warehouse-list-create"),
    path("warehouses/<uuid:warehouse_id>/", WarehouseDetailView.as_view(), name="warehouse-detail"),
    path(
        "warehouses/<uuid:warehouse_id>/locations/",
        StorageLocationCreateView.as_view(),
        name="storage-location-create",
    ),
    # Stock Balances & Reconciliation
    path("balances/", StockBalanceListView.as_view(), name="stock-balance-list"),
    path("balances/reconciliation/", ReconciliationView.as_view(), name="stock-reconciliation"),
    # Stock Ledger Movements
    path("ledger/", StockLedgerListView.as_view(), name="stock-ledger-list"),
    # Stock Alerts (low stock & expiring batches)
    path("alerts/", StockAlertsView.as_view(), name="stock-alerts"),
    # Stock Transactions (Commands & Detail)
    path("transactions/<uuid:pk>/", StockTransactionDetailView.as_view(), name="transaction-detail"),
    path("transactions/receipt-opening/", ReceiveOpeningStockView.as_view(), name="receipt-opening"),
    path("transactions/receipt-donation/", ReceiveDonationView.as_view(), name="receipt-donation"),
    path("transactions/receive-purchase/", ReceivePurchasedStockView.as_view(), name="receipt-purchase"),
    path("transactions/transfer/", TransferStockView.as_view(), name="transfer-stock"),
    path("transactions/issue/", IssueStockView.as_view(), name="issue-stock"),
    path("transactions/adjust/", AdjustStockView.as_view(), name="adjust-stock"),
    path("transactions/write-off/", WriteOffStockView.as_view(), name="write-off-stock"),
    # Pending Procurement GRNs for Stock Intake
    path("pending-grns/", PendingGRNsListView.as_view(), name="pending-grns-list"),
]
