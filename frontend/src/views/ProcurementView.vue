<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { api } from "@/api/client";
import { useTenantStore } from "@/stores/tenant";
import type {
  GoodsReceiptNote,
  PurchaseOrder,
  PurchaseRequisition,
  RequisitionFulfillment,
  Vendor,
} from "@/types/procurement";

const tenantStore = useTenantStore();

const activeTab = ref<"requisitions" | "orders" | "receipts" | "vendors">("requisitions");
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);

// Data lists
const vendors = ref<Vendor[]>([]);
const requisitions = ref<PurchaseRequisition[]>([]);
const purchaseOrders = ref<PurchaseOrder[]>([]);
const goodsReceipts = ref<GoodsReceiptNote[]>([]);

// Selected / Detail state
const selectedRequisition = ref<PurchaseRequisition | null>(null);
const selectedFulfillment = ref<RequisitionFulfillment | null>(null);
const selectedOrder = ref<PurchaseOrder | null>(null);
const selectedGrn = ref<GoodsReceiptNote | null>(null);

// Attention panel metrics
const pendingRequisitions = computed(() =>
  requisitions.value.filter((r) => r.authorization_status === "submitted")
);
const openOrders = computed(() =>
  purchaseOrders.value.filter((o) => o.status === "issued")
);
const uninspectedReceipts = computed(() =>
  goodsReceipts.value.filter((g) => !g.is_fully_inspected)
);

// ── Requisition Form State ──
const isCreatingRequisition = ref(false);
const reqTitle = ref("");
const reqCurrency = ref("USD");
const reqNotes = ref("");
interface ReqFormLine {
  description: string;
  quantity: number;
  unit: string;
  estimated_unit_price: number;
}
const reqLines = ref<ReqFormLine[]>([
  { description: "", quantity: 1, unit: "each", estimated_unit_price: 0 },
]);

function addReqLine() {
  reqLines.value.push({ description: "", quantity: 1, unit: "each", estimated_unit_price: 0 });
}
function removeReqLine(index: number) {
  if (reqLines.value.length > 1) {
    reqLines.value.splice(index, 1);
  }
}
const reqEstimatedTotal = computed(() =>
  reqLines.value.reduce((acc, l) => acc + (Number(l.quantity) || 0) * (Number(l.estimated_unit_price) || 0), 0)
);

// ── Purchase Order Form State ──
const isCreatingOrder = ref(false);
const orderVendorId = ref("");
const orderRequisitionId = ref("");
const orderCurrency = ref("USD");
const orderDeliveryDate = ref("");
const orderDeliveryAddress = ref("");
const orderNotes = ref("");
interface OrderFormLine {
  description: string;
  quantity: number;
  unit: string;
  unit_price: number;
  requisition_item_id?: string;
}
const orderLines = ref<OrderFormLine[]>([
  { description: "", quantity: 1, unit: "each", unit_price: 0 },
]);

function addOrderLine() {
  orderLines.value.push({ description: "", quantity: 1, unit: "each", unit_price: 0 });
}
function removeOrderLine(index: number) {
  if (orderLines.value.length > 1) {
    orderLines.value.splice(index, 1);
  }
}

// ── Goods Receipt Form State ──
const isRecordingReceipt = ref(false);
const receiptOrderId = ref("");
const receiptDate = ref(new Date().toISOString().split("T")[0]);
const receiptType = ref<"goods" | "services">("goods");
const receiptNotes = ref("");
interface ReceiptFormLine {
  po_item_id: string;
  description: string;
  quantity_received: number;
}
const receiptLines = ref<ReceiptFormLine[]>([]);

// ── Inspection Form State ──
const isInspectingReceipt = ref(false);
interface InspectionFormLine {
  grn_item_id: string;
  description: string;
  quantity_received: number;
  quantity_accepted: number;
  quantity_rejected: number;
  rejection_reason: string;
}
const inspectionLines = ref<InspectionFormLine[]>([]);

// ── Vendor Form State ──
const isCreatingVendor = ref(false);
const vendorName = ref("");
const vendorType = ref<"goods" | "services" | "consulting">("goods");
const vendorTaxId = ref("");
const vendorCountry = ref("");
const vendorContact = ref("");
const vendorEmail = ref("");
const vendorPhone = ref("");
const vendorTerms = ref("Net 30");

// ── Load All Data ──
async function loadData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  errorMessage.value = null;
  try {
    const [vList, rList, oList, grnList] = await Promise.all([
      api.get<Vendor[]>("/api/v1/procurement/vendors/"),
      api.get<PurchaseRequisition[]>("/api/v1/procurement/requisitions/"),
      api.get<PurchaseOrder[]>("/api/v1/procurement/orders/"),
      api.get<GoodsReceiptNote[]>("/api/v1/procurement/receipts/"),
    ]);
    vendors.value = vList;
    requisitions.value = rList;
    purchaseOrders.value = oList;
    goodsReceipts.value = grnList;
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to load procurement data.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadData();
});

watch(
  () => tenantStore.currentOrganizationId,
  () => {
    loadData();
  }
);

// ── Actions: Requisitions ──
async function submitNewRequisition() {
  if (!reqTitle.value.trim()) {
    errorMessage.value = "Requisition title is required.";
    return;
  }
  isLoading.value = true;
  errorMessage.value = null;
  try {
    await api.post("/api/v1/procurement/requisitions/", {
      title: reqTitle.value.trim(),
      currency: reqCurrency.value,
      notes: reqNotes.value.trim(),
      items: reqLines.value.map((l) => ({
        description: l.description,
        quantity: l.quantity,
        unit: l.unit,
        estimated_unit_price: l.estimated_unit_price,
      })),
    });
    successMessage.value = "Purchase requisition created successfully.";
    isCreatingRequisition.value = false;
    reqTitle.value = "";
    reqLines.value = [{ description: "", quantity: 1, unit: "each", estimated_unit_price: 0 }];
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to create requisition.";
  } finally {
    isLoading.value = false;
  }
}

async function handleActionRequisition(id: string, action: "submit" | "approve" | "return") {
  isLoading.value = true;
  errorMessage.value = null;
  try {
    await api.post(`/api/v1/procurement/requisitions/${id}/${action}/`, {});
    successMessage.value = `Requisition ${action}ted successfully.`;
    await loadData();
    if (selectedRequisition.value?.id === id) {
      await viewRequisitionDetail(id);
    }
  } catch (err: any) {
    errorMessage.value = err.message || `Failed to ${action} requisition.`;
  } finally {
    isLoading.value = false;
  }
}

async function viewRequisitionDetail(id: string) {
  try {
    const [detail, fulf] = await Promise.all([
      api.get<PurchaseRequisition>(`/api/v1/procurement/requisitions/${id}/`),
      api.get<RequisitionFulfillment>(`/api/v1/procurement/requisitions/${id}/fulfillment/`),
    ]);
    selectedRequisition.value = detail;
    selectedFulfillment.value = fulf;
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to load requisition detail.";
  }
}

// ── Actions: Purchase Orders ──
async function submitNewOrder() {
  if (!orderVendorId.value) {
    errorMessage.value = "Supplier is required.";
    return;
  }
  isLoading.value = true;
  errorMessage.value = null;
  try {
    await api.post("/api/v1/procurement/orders/", {
      vendor_id: orderVendorId.value,
      requisition_id: orderRequisitionId.value || null,
      currency: orderCurrency.value,
      expected_delivery_date: orderDeliveryDate.value || null,
      delivery_address: orderDeliveryAddress.value.trim(),
      notes: orderNotes.value.trim(),
      items: orderLines.value.map((l) => ({
        description: l.description,
        quantity: l.quantity,
        unit: l.unit,
        unit_price: l.unit_price,
        allocations: l.requisition_item_id
          ? [{ requisition_item_id: l.requisition_item_id, allocated_quantity: l.quantity }]
          : [],
      })),
    });
    successMessage.value = "Purchase order created in draft.";
    isCreatingOrder.value = false;
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to create order.";
  } finally {
    isLoading.value = false;
  }
}

async function handleActionOrder(id: string, action: "issue" | "close") {
  isLoading.value = true;
  errorMessage.value = null;
  try {
    await api.post(`/api/v1/procurement/orders/${id}/${action}/`, {});
    successMessage.value = `Purchase order ${action}d successfully.`;
    await loadData();
    if (selectedOrder.value?.id === id) {
      await viewOrderDetail(id);
    }
  } catch (err: any) {
    errorMessage.value = err.message || `Failed to ${action} order.`;
  } finally {
    isLoading.value = false;
  }
}

async function viewOrderDetail(id: string) {
  try {
    selectedOrder.value = await api.get<PurchaseOrder>(`/api/v1/procurement/orders/${id}/`);
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to load order detail.";
  }
}

// ── Actions: Goods Receipts ──
function prepareReceiptForm(po: PurchaseOrder) {
  receiptOrderId.value = po.id;
  receiptLines.value = (po.items || []).map((it) => ({
    po_item_id: it.id,
    description: it.description,
    quantity_received: Number(it.quantity_outstanding || it.quantity),
  }));
  isRecordingReceipt.value = true;
  activeTab.value = "receipts";
}

async function submitGoodsReceipt() {
  if (!receiptOrderId.value) return;
  isLoading.value = true;
  errorMessage.value = null;
  try {
    await api.post("/api/v1/procurement/receipts/", {
      purchase_order_id: receiptOrderId.value,
      received_date: receiptDate.value,
      receipt_type: receiptType.value,
      inspection_notes: receiptNotes.value.trim(),
      items: receiptLines.value.map((l) => ({
        po_item_id: l.po_item_id,
        quantity_received: l.quantity_received,
      })),
    });
    successMessage.value = "Goods receipt note recorded successfully.";
    isRecordingReceipt.value = false;
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to record goods receipt.";
  } finally {
    isLoading.value = false;
  }
}

async function openInspectModal(grn: GoodsReceiptNote) {
  try {
    const fullGrn = await api.get<GoodsReceiptNote>(`/api/v1/procurement/receipts/${grn.id}/`);
    selectedGrn.value = fullGrn;
    inspectionLines.value = (fullGrn.items || []).map((item) => ({
      grn_item_id: item.id,
      description: item.description || "PO Line Item",
      quantity_received: Number(item.quantity_received),
      quantity_accepted: Number(item.quantity_received),
      quantity_rejected: 0,
      rejection_reason: "",
    }));
    isInspectingReceipt.value = true;
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to load receipt for inspection.";
  }
}

async function submitInspection() {
  if (!selectedGrn.value) return;
  isLoading.value = true;
  errorMessage.value = null;
  try {
    await api.post(`/api/v1/procurement/receipts/${selectedGrn.value.id}/inspect/`, {
      inspections: inspectionLines.value.map((l) => ({
        grn_item_id: l.grn_item_id,
        quantity_accepted: l.quantity_accepted,
        quantity_rejected: l.quantity_rejected,
        rejection_reason: l.rejection_reason,
      })),
    });
    successMessage.value = "Inspection recorded and reconciliation finalized.";
    isInspectingReceipt.value = false;
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to submit inspection.";
  } finally {
    isLoading.value = false;
  }
}

// ── Actions: Vendors ──
async function submitNewVendor() {
  if (!vendorName.value.trim()) {
    errorMessage.value = "Vendor name is required.";
    return;
  }
  isLoading.value = true;
  errorMessage.value = null;
  try {
    await api.post("/api/v1/procurement/vendors/", {
      name: vendorName.value.trim(),
      vendor_type: vendorType.value,
      tax_id: vendorTaxId.value.trim(),
      country: vendorCountry.value.trim(),
      contact_name: vendorContact.value.trim(),
      email: vendorEmail.value.trim(),
      phone: vendorPhone.value.trim(),
      default_payment_terms: vendorTerms.value.trim(),
    });
    successMessage.value = "Vendor created successfully.";
    isCreatingVendor.value = false;
    vendorName.value = "";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to create vendor.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="procurement-view">
    <!-- Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">Procurement & Purchasing</h1>
        <p class="page-subtitle">
          Manage suppliers, operational purchase requests, commercial orders, and delivery verification.
        </p>
      </div>
      <div class="header-actions">
        <button
          v-if="activeTab === 'requisitions'"
          class="btn btn-primary"
          @click="isCreatingRequisition = true"
        >
          + Raise Requisition
        </button>
        <button
          v-if="activeTab === 'orders'"
          class="btn btn-primary"
          @click="isCreatingOrder = true"
        >
          + Create Purchase Order
        </button>
        <button
          v-if="activeTab === 'vendors'"
          class="btn btn-primary"
          @click="isCreatingVendor = true"
        >
          + Add Supplier
        </button>
      </div>
    </header>

    <!-- Feedback Alerts -->
    <div v-if="errorMessage" class="alert alert-error">
      <span>{{ errorMessage }}</span>
      <button class="alert-dismiss" @click="errorMessage = null">✕</button>
    </div>
    <div v-if="successMessage" class="alert alert-success">
      <span>{{ successMessage }}</span>
      <button class="alert-dismiss" @click="successMessage = null">✕</button>
    </div>

    <!-- Operational Attention Panel -->
    <section class="attention-panel" aria-label="Operational Attention">
      <div class="attention-card" :class="{ 'attention-active': pendingRequisitions.length > 0 }">
        <div class="attention-icon">⏳</div>
        <div class="attention-body">
          <div class="attention-count">{{ pendingRequisitions.length }}</div>
          <div class="attention-label">Requisitions Awaiting Approval</div>
        </div>
      </div>
      <div class="attention-card" :class="{ 'attention-active': openOrders.length > 0 }">
        <div class="attention-icon">🚚</div>
        <div class="attention-body">
          <div class="attention-count">{{ openOrders.length }}</div>
          <div class="attention-label">Orders Awaiting Delivery</div>
        </div>
      </div>
      <div class="attention-card" :class="{ 'attention-active': uninspectedReceipts.length > 0 }">
        <div class="attention-icon">🔍</div>
        <div class="attention-body">
          <div class="attention-count">{{ uninspectedReceipts.length }}</div>
          <div class="attention-label">Receipts Pending Inspection</div>
        </div>
      </div>
    </section>

    <!-- Workspace Tabs Navigation -->
    <nav class="tabs-nav" aria-label="Procurement Sections">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'requisitions' }"
        @click="activeTab = 'requisitions'"
      >
        Requisitions ({{ requisitions.length }})
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'orders' }"
        @click="activeTab = 'orders'"
      >
        Purchasing & Orders ({{ purchaseOrders.length }})
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'receipts' }"
        @click="activeTab = 'receipts'"
      >
        Goods Receipts ({{ goodsReceipts.length }})
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'vendors' }"
        @click="activeTab = 'vendors'"
      >
        Suppliers & Directory ({{ vendors.length }})
      </button>
    </nav>

    <!-- TAB 1: REQUISITIONS -->
    <div v-if="activeTab === 'requisitions'" class="tab-content">
      <!-- Create Requisition Modal -->
      <div v-if="isCreatingRequisition" class="modal-backdrop">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Raise Purchase Requisition</h3>
            <button class="modal-close" @click="isCreatingRequisition = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Requisition Title / Purpose</label>
              <input v-model="reqTitle" type="text" placeholder="e.g. Q1 Dormitory Food Supplies" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Currency</label>
                <input v-model="reqCurrency" type="text" maxlength="3" />
              </div>
              <div class="form-group">
                <label>Estimated Total</label>
                <div class="static-value">{{ reqCurrency }} {{ reqEstimatedTotal.toFixed(2) }}</div>
              </div>
            </div>

            <div class="items-editor">
              <div class="items-header">
                <h4>Line Items</h4>
                <button type="button" class="btn btn-sm btn-secondary" @click="addReqLine">+ Add Item</button>
              </div>
              <div v-for="(line, idx) in reqLines" :key="idx" class="item-row">
                <input v-model="line.description" type="text" placeholder="Item description" class="flex-2" />
                <input v-model.number="line.quantity" type="number" min="1" placeholder="Qty" class="flex-1" />
                <input v-model="line.unit" type="text" placeholder="Unit (pcs, bags)" class="flex-1" />
                <input v-model.number="line.estimated_unit_price" type="number" min="0" step="0.01" placeholder="Est. Price" class="flex-1" />
                <button type="button" class="btn-icon" title="Remove" @click="removeReqLine(idx)">🗑️</button>
              </div>
            </div>

            <div class="form-group">
              <label>Notes & Justification</label>
              <textarea v-model="reqNotes" rows="2" placeholder="Program activity context, justification..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="isCreatingRequisition = false">Cancel</button>
            <button class="btn btn-primary" :disabled="isLoading" @click="submitNewRequisition">
              Create Requisition
            </button>
          </div>
        </div>
      </div>

      <!-- Requisition List Table -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Number</th>
              <th>Title</th>
              <th>Authorization</th>
              <th>Est. Cost</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="requisitions.length === 0">
              <td colspan="6" class="text-center text-muted">No purchase requisitions found.</td>
            </tr>
            <tr v-for="r in requisitions" :key="r.id">
              <td class="font-mono">{{ r.requisition_number }}</td>
              <td><strong>{{ r.title }}</strong></td>
              <td>
                <span class="badge" :class="'badge-' + r.authorization_status">
                  {{ r.authorization_status.toUpperCase() }}
                </span>
              </td>
              <td>{{ r.currency }} {{ Number(r.total_estimated_cost).toFixed(2) }}</td>
              <td>{{ new Date(r.created_at).toLocaleDateString() }}</td>
              <td>
                <div class="actions-cell">
                  <button class="btn btn-xs btn-outline" @click="viewRequisitionDetail(r.id)">View</button>
                  <button
                    v-if="r.authorization_status === 'draft'"
                    class="btn btn-xs btn-secondary"
                    @click="handleActionRequisition(r.id, 'submit')"
                  >
                    Submit
                  </button>
                  <button
                    v-if="r.authorization_status === 'submitted'"
                    class="btn btn-xs btn-success"
                    @click="handleActionRequisition(r.id, 'approve')"
                  >
                    Approve
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Requisition Detail Drawer/Modal -->
      <div v-if="selectedRequisition" class="detail-card">
        <div class="detail-header">
          <div>
            <h3>{{ selectedRequisition.requisition_number }}: {{ selectedRequisition.title }}</h3>
            <span class="badge" :class="'badge-' + selectedRequisition.authorization_status">
              {{ selectedRequisition.authorization_status.toUpperCase() }}
            </span>
            <span v-if="selectedFulfillment" class="badge badge-outline ml-2">
              Fulfillment: {{ selectedFulfillment.fulfillment_position }}
            </span>
          </div>
          <button class="btn-icon" @click="selectedRequisition = null">✕</button>
        </div>
        <div class="detail-body">
          <table class="data-table">
            <thead>
              <tr>
                <th>Description</th>
                <th>Requested</th>
                <th>Est. Unit Price</th>
                <th>Line Total</th>
                <th>Ordered</th>
                <th>Outstanding</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in selectedRequisition.items || []" :key="item.id">
                <td>{{ item.description }}</td>
                <td>{{ item.quantity }} {{ item.unit }}</td>
                <td>{{ selectedRequisition.currency }} {{ Number(item.estimated_unit_price).toFixed(2) }}</td>
                <td>{{ selectedRequisition.currency }} {{ Number(item.line_total).toFixed(2) }}</td>
                <td>{{ item.allocated_quantity || 0 }} {{ item.unit }}</td>
                <td><strong>{{ item.outstanding_quantity ?? item.quantity }} {{ item.unit }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 2: PURCHASING & ORDERS -->
    <div v-if="activeTab === 'orders'" class="tab-content">
      <!-- Create PO Modal -->
      <div v-if="isCreatingOrder" class="modal-backdrop">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Issue Purchase Order</h3>
            <button class="modal-close" @click="isCreatingOrder = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-row">
              <div class="form-group flex-2">
                <label>Supplier / Vendor</label>
                <select v-model="orderVendorId">
                  <option value="" disabled>Select supplier</option>
                  <option v-for="v in vendors" :key="v.id" :value="v.id">{{ v.name }} ({{ v.default_currency }})</option>
                </select>
              </div>
              <div class="form-group flex-1">
                <label>Against Requisition (Optional)</label>
                <select v-model="orderRequisitionId">
                  <option value="">None (Direct Order)</option>
                  <option
                    v-for="r in requisitions.filter(r => r.authorization_status === 'approved')"
                    :key="r.id"
                    :value="r.id"
                  >
                    {{ r.requisition_number }} - {{ r.title }}
                  </option>
                </select>
              </div>
            </div>

            <div class="items-editor">
              <div class="items-header">
                <h4>Contracted Line Items</h4>
                <button type="button" class="btn btn-sm btn-secondary" @click="addOrderLine">+ Add Item</button>
              </div>
              <div v-for="(line, idx) in orderLines" :key="idx" class="item-row">
                <input v-model="line.description" type="text" placeholder="Description" class="flex-2" />
                <input v-model.number="line.quantity" type="number" min="1" placeholder="Qty" class="flex-1" />
                <input v-model="line.unit" type="text" placeholder="Unit" class="flex-1" />
                <input v-model.number="line.unit_price" type="number" min="0" step="0.01" placeholder="Price" class="flex-1" />
                <button type="button" class="btn-icon" @click="removeOrderLine(idx)">🗑️</button>
              </div>
            </div>

            <div class="form-group">
              <label>Delivery Address</label>
              <input v-model="orderDeliveryAddress" type="text" placeholder="Warehouse / Branch Address" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="isCreatingOrder = false">Cancel</button>
            <button class="btn btn-primary" :disabled="isLoading" @click="submitNewOrder">
              Save Draft Order
            </button>
          </div>
        </div>
      </div>

      <!-- PO List Table -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Supplier</th>
              <th>Status</th>
              <th>Total Commitment</th>
              <th>Payment Terms</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="purchaseOrders.length === 0">
              <td colspan="6" class="text-center text-muted">No purchase orders recorded.</td>
            </tr>
            <tr v-for="o in purchaseOrders" :key="o.id">
              <td class="font-mono"><strong>{{ o.order_number }}</strong></td>
              <td>{{ o.vendor_name }}</td>
              <td>
                <span class="badge" :class="'badge-' + o.status">
                  {{ o.status.toUpperCase() }}
                </span>
              </td>
              <td>{{ o.currency }} {{ Number(o.total_amount).toFixed(2) }}</td>
              <td>{{ o.payment_terms || 'Standard' }}</td>
              <td>
                <div class="actions-cell">
                  <button class="btn btn-xs btn-outline" @click="viewOrderDetail(o.id)">Details</button>
                  <button
                    v-if="o.status === 'draft'"
                    class="btn btn-xs btn-success"
                    @click="handleActionOrder(o.id, 'issue')"
                  >
                    Issue
                  </button>
                  <button
                    v-if="o.status === 'issued'"
                    class="btn btn-xs btn-primary"
                    @click="prepareReceiptForm(o)"
                  >
                    Receive Delivery
                  </button>
                  <button
                    v-if="o.status === 'issued'"
                    class="btn btn-xs btn-secondary"
                    @click="handleActionOrder(o.id, 'close')"
                  >
                    Close
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Order Detail Card -->
      <div v-if="selectedOrder" class="detail-card">
        <div class="detail-header">
          <div>
            <h3>PO {{ selectedOrder.order_number }} — {{ selectedOrder.vendor_name }}</h3>
            <span class="badge" :class="'badge-' + selectedOrder.status">{{ selectedOrder.status.toUpperCase() }}</span>
          </div>
          <button class="btn-icon" @click="selectedOrder = null">✕</button>
        </div>
        <div class="detail-body">
          <table class="data-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Ordered</th>
                <th>Unit Price</th>
                <th>Line Total</th>
                <th>Received</th>
                <th>Accepted</th>
                <th>Outstanding</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="it in selectedOrder.items || []" :key="it.id">
                <td>{{ it.description }}</td>
                <td>{{ it.quantity }} {{ it.unit }}</td>
                <td>{{ selectedOrder.currency }} {{ Number(it.unit_price).toFixed(2) }}</td>
                <td>{{ selectedOrder.currency }} {{ Number(it.line_total).toFixed(2) }}</td>
                <td>{{ it.quantity_received || 0 }}</td>
                <td>{{ it.quantity_accepted || 0 }}</td>
                <td><strong>{{ it.quantity_outstanding || 0 }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: GOODS RECEIPTS -->
    <div v-if="activeTab === 'receipts'" class="tab-content">
      <!-- Record Receipt Modal -->
      <div v-if="isRecordingReceipt" class="modal-backdrop">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Record Delivery Receipt (GRN)</h3>
            <button class="modal-close" @click="isRecordingReceipt = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-row">
              <div class="form-group flex-1">
                <label>Received Date</label>
                <input v-model="receiptDate" type="date" />
              </div>
              <div class="form-group flex-1">
                <label>Receipt Type</label>
                <select v-model="receiptType">
                  <option value="goods">Physical Goods</option>
                  <option value="services">Service Completion</option>
                </select>
              </div>
            </div>

            <div class="items-editor">
              <h4>Received Quantities</h4>
              <div v-for="(line, idx) in receiptLines" :key="idx" class="item-row">
                <div class="flex-2">{{ line.description }}</div>
                <input v-model.number="line.quantity_received" type="number" min="0" placeholder="Count received" class="flex-1" />
              </div>
            </div>

            <div class="form-group">
              <label>Delivery / Waybill Notes</label>
              <textarea v-model="receiptNotes" rows="2" placeholder="Carrier details, condition on arrival..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="isRecordingReceipt = false">Cancel</button>
            <button class="btn btn-primary" :disabled="isLoading" @click="submitGoodsReceipt">
              Save Goods Receipt
            </button>
          </div>
        </div>
      </div>

      <!-- Inspect Receipt Modal -->
      <div v-if="isInspectingReceipt && selectedGrn" class="modal-backdrop">
        <div class="modal-card modal-lg">
          <div class="modal-header">
            <h3>Inspection & Quantity Reconciliation — {{ selectedGrn.receipt_number }}</h3>
            <button class="modal-close" @click="isInspectingReceipt = false">✕</button>
          </div>
          <div class="modal-body">
            <p class="text-sm text-muted mb-4">
              Accepted + Rejected quantities must exactly equal the received physical count.
            </p>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Received</th>
                  <th>Accepted</th>
                  <th>Rejected</th>
                  <th>Rejection Reason</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(line, idx) in inspectionLines" :key="idx">
                  <td>{{ line.description }}</td>
                  <td><strong>{{ line.quantity_received }}</strong></td>
                  <td>
                    <input v-model.number="line.quantity_accepted" type="number" min="0" class="input-sm" />
                  </td>
                  <td>
                    <input v-model.number="line.quantity_rejected" type="number" min="0" class="input-sm" />
                  </td>
                  <td>
                    <input v-model="line.rejection_reason" type="text" placeholder="Required if rejected" class="input-sm" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="isInspectingReceipt = false">Cancel</button>
            <button class="btn btn-success" :disabled="isLoading" @click="submitInspection">
              Finalize Inspection
            </button>
          </div>
        </div>
      </div>

      <!-- GRN List Table -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Receipt #</th>
              <th>Order #</th>
              <th>Type</th>
              <th>Date</th>
              <th>Inspection State</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="goodsReceipts.length === 0">
              <td colspan="6" class="text-center text-muted">No goods receipt notes recorded.</td>
            </tr>
            <tr v-for="g in goodsReceipts" :key="g.id">
              <td class="font-mono"><strong>{{ g.receipt_number }}</strong></td>
              <td>{{ g.order_number }}</td>
              <td>{{ g.receipt_type.toUpperCase() }}</td>
              <td>{{ g.received_date }}</td>
              <td>
                <span v-if="g.is_fully_inspected" class="badge badge-success">
                  {{ g.has_rejections ? 'INSPECTED (REJECTIONS)' : 'INSPECTED (ACCEPTED)' }}
                </span>
                <span v-else class="badge badge-warning">PENDING INSPECTION</span>
              </td>
              <td>
                <button
                  v-if="!g.is_fully_inspected"
                  class="btn btn-xs btn-primary"
                  @click="openInspectModal(g)"
                >
                  Inspect & Reconcile
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: SUPPLIERS & DIRECTORY -->
    <div v-if="activeTab === 'vendors'" class="tab-content">
      <!-- Create Vendor Modal -->
      <div v-if="isCreatingVendor" class="modal-backdrop">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Add New Supplier / Vendor</h3>
            <button class="modal-close" @click="isCreatingVendor = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-row">
              <div class="form-group flex-2">
                <label>Vendor Name</label>
                <input v-model="vendorName" type="text" placeholder="e.g. Acme Pharmaceuticals Ltd" />
              </div>
              <div class="form-group flex-1">
                <label>Classification</label>
                <select v-model="vendorType">
                  <option value="goods">Goods Supplier</option>
                  <option value="services">Service Contractor</option>
                  <option value="consulting">Professional Consulting</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group flex-1">
                <label>Tax ID / Registration</label>
                <input v-model="vendorTaxId" type="text" placeholder="TIN / VAT" />
              </div>
              <div class="form-group flex-1">
                <label>Default Terms</label>
                <input v-model="vendorTerms" type="text" placeholder="e.g. Net 30" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group flex-1">
                <label>Contact Person</label>
                <input v-model="vendorContact" type="text" />
              </div>
              <div class="form-group flex-1">
                <label>Email</label>
                <input v-model="vendorEmail" type="email" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="isCreatingVendor = false">Cancel</button>
            <button class="btn btn-primary" :disabled="isLoading" @click="submitNewVendor">
              Save Supplier
            </button>
          </div>
        </div>
      </div>

      <!-- Vendor List Table -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Tax ID</th>
              <th>Contact</th>
              <th>Email</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="vendors.length === 0">
              <td colspan="6" class="text-center text-muted">No suppliers registered.</td>
            </tr>
            <tr v-for="v in vendors" :key="v.id">
              <td><strong>{{ v.name }}</strong></td>
              <td>{{ v.vendor_type }}</td>
              <td class="font-mono">{{ v.tax_id || '-' }}</td>
              <td>{{ v.contact_name || '-' }}</td>
              <td>{{ v.email || '-' }}</td>
              <td>
                <span class="badge" :class="v.is_active ? 'badge-success' : 'badge-danger'">
                  {{ v.is_active ? 'ACTIVE' : 'DEACTIVATED' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.procurement-view {
  padding: 1.5rem;
  max-width: 1300px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 0.25rem;
}

.page-subtitle {
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

/* Attention Panel */
.attention-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.attention-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.attention-active {
  border-left: 4px solid var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 4%, var(--color-surface));
}

.attention-icon {
  font-size: 2rem;
}

.attention-count {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-main);
}

.attention-label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

/* Tabs */
.tabs-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-muted);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--color-text-main);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

/* Table */
.table-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.data-table th {
  background: var(--color-background);
  color: var(--color-text-muted);
  font-weight: 600;
}

.actions-cell {
  display: flex;
  gap: 0.4rem;
}

/* Badges */
.badge {
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.badge-draft { background: #e2e8f0; color: #475569; }
.badge-submitted { background: #fef3c7; color: #b45309; }
.badge-approved { background: #dcfce7; color: #15803d; }
.badge-issued { background: #dbeafe; color: #1d4ed8; }
.badge-closed { background: #f1f5f9; color: #64748b; }
.badge-cancelled { background: #fee2e2; color: #b91c1c; }
.badge-success { background: #dcfce7; color: #15803d; }
.badge-warning { background: #fef3c7; color: #b45309; }
.badge-danger { background: #fee2e2; color: #b91c1c; }
.badge-outline { border: 1px solid var(--color-border); color: var(--color-text-muted); }

/* Detail Card */
.detail-card {
  margin-top: 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-lg {
  max-width: 850px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-body {
  padding: 1.25rem;
}

.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Forms */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.35rem;
  color: var(--color-text-muted);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  color: var(--color-text-main);
  font-size: 0.9rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.flex-1 { flex: 1; }
.flex-2 { flex: 2; }

.items-editor {
  margin: 1.25rem 0;
  padding: 1rem;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.item-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.5rem;
}

.item-row input {
  padding: 0.45rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  font-size: 0.85rem;
}

.input-sm {
  padding: 0.3rem 0.5rem;
  width: 90px;
}

/* Buttons */
.btn {
  padding: 0.6rem 1rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { opacity: 0.9; }
.btn-secondary { background: var(--color-border); color: var(--color-text-main); }
.btn-success { background: #16a34a; color: white; }
.btn-outline { border: 1px solid var(--color-border); background: transparent; color: var(--color-text-main); }
.btn-xs { padding: 0.25rem 0.5rem; font-size: 0.75rem; }
.btn-sm { padding: 0.4rem 0.75rem; font-size: 0.8rem; }

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
}

/* Alerts */
.alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
}
.alert-error { background: #fee2e2; color: #b91c1c; }
.alert-success { background: #dcfce7; color: #15803d; }
.alert-dismiss { background: none; border: none; cursor: pointer; }
</style>
