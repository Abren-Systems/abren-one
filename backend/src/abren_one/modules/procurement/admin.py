from django.contrib import admin

from abren_one.modules.procurement.models.goods_receipt import (
    GoodsReceiptItem,
    GoodsReceiptNote,
)
from abren_one.modules.procurement.models.order_line_allocation import OrderLineAllocation
from abren_one.modules.procurement.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
)
from abren_one.modules.procurement.models.purchase_requisition import (
    PurchaseRequisition,
    RequisitionItem,
)
from abren_one.modules.procurement.models.vendor import Vendor


class RequisitionItemInline(admin.TabularInline):
    model = RequisitionItem
    extra = 1
    fields = ("description", "quantity", "unit", "estimated_unit_price", "program_id")


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ("description", "quantity", "unit", "unit_price")


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 1
    fields = (
        "po_item",
        "quantity_received",
        "quantity_accepted",
        "quantity_rejected",
        "is_inspected",
        "rejection_reason",
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "vendor_type",
        "tax_id",
        "contact_name",
        "email",
        "is_active",
        "organization",
    )
    list_filter = ("vendor_type", "is_active", "verification_status")
    search_fields = ("name", "tax_id", "email", "contact_name")


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = (
        "requisition_number",
        "title",
        "authorization_status",
        "currency",
        "requested_by",
        "organization",
    )
    list_filter = ("authorization_status", "currency")
    search_fields = ("requisition_number", "title")
    inlines = [RequisitionItemInline]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "vendor",
        "status",
        "currency",
        "issued_at",
        "organization",
    )
    list_filter = ("status", "currency")
    search_fields = ("order_number", "vendor__name")
    inlines = [PurchaseOrderItemInline]


@admin.register(OrderLineAllocation)
class OrderLineAllocationAdmin(admin.ModelAdmin):
    list_display = ("id", "requisition_item", "po_item", "allocated_quantity")


@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "purchase_order",
        "receipt_type",
        "received_date",
        "is_correction",
        "organization",
    )
    list_filter = ("receipt_type", "is_correction", "received_date")
    search_fields = ("receipt_number", "purchase_order__order_number")
    inlines = [GoodsReceiptItemInline]
