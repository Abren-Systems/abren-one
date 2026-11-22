from django.urls import path

from abren_one.modules.procurement.interfaces.api.v1.views import (
    ApproveRequisitionView,
    CancelPurchaseOrderView,
    ClosePurchaseOrderView,
    DeactivateVendorView,
    GoodsReceiptDetailView,
    GoodsReceiptListCreateView,
    InspectGoodsReceiptView,
    IssuePurchaseOrderView,
    OrderDeliveryPositionView,
    PurchaseOrderDetailUpdateView,
    PurchaseOrderListCreateView,
    RejectRequisitionView,
    RequisitionDetailUpdateView,
    RequisitionFulfillmentView,
    RequisitionListCreateView,
    ReturnRequisitionView,
    SubmitRequisitionView,
    VendorDetailUpdateView,
    VendorListCreateView,
)

app_name = "procurement"

urlpatterns = [
    # Vendors
    path("vendors/", VendorListCreateView.as_view(), name="vendor-list-create"),
    path("vendors/<uuid:vendor_id>/", VendorDetailUpdateView.as_view(), name="vendor-detail"),
    path(
        "vendors/<uuid:vendor_id>/deactivate/",
        DeactivateVendorView.as_view(),
        name="vendor-deactivate",
    ),
    # Purchase Requisitions
    path("requisitions/", RequisitionListCreateView.as_view(), name="requisition-list-create"),
    path(
        "requisitions/<uuid:requisition_id>/",
        RequisitionDetailUpdateView.as_view(),
        name="requisition-detail",
    ),
    path(
        "requisitions/<uuid:requisition_id>/submit/",
        SubmitRequisitionView.as_view(),
        name="requisition-submit",
    ),
    path(
        "requisitions/<uuid:requisition_id>/approve/",
        ApproveRequisitionView.as_view(),
        name="requisition-approve",
    ),
    path(
        "requisitions/<uuid:requisition_id>/reject/",
        RejectRequisitionView.as_view(),
        name="requisition-reject",
    ),
    path(
        "requisitions/<uuid:requisition_id>/return/",
        ReturnRequisitionView.as_view(),
        name="requisition-return",
    ),
    path(
        "requisitions/<uuid:requisition_id>/fulfillment/",
        RequisitionFulfillmentView.as_view(),
        name="requisition-fulfillment",
    ),
    # Purchase Orders
    path("orders/", PurchaseOrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<uuid:order_id>/", PurchaseOrderDetailUpdateView.as_view(), name="order-detail"),
    path("orders/<uuid:order_id>/issue/", IssuePurchaseOrderView.as_view(), name="order-issue"),
    path("orders/<uuid:order_id>/cancel/", CancelPurchaseOrderView.as_view(), name="order-cancel"),
    path("orders/<uuid:order_id>/close/", ClosePurchaseOrderView.as_view(), name="order-close"),
    path(
        "orders/<uuid:order_id>/delivery-position/",
        OrderDeliveryPositionView.as_view(),
        name="order-delivery-position",
    ),
    # Goods Receipts
    path("receipts/", GoodsReceiptListCreateView.as_view(), name="receipt-list-create"),
    path(
        "receipts/<uuid:receipt_id>/",
        GoodsReceiptDetailView.as_view(),
        name="receipt-detail",
    ),
    path(
        "receipts/<uuid:receipt_id>/inspect/",
        InspectGoodsReceiptView.as_view(),
        name="receipt-inspect",
    ),
]
