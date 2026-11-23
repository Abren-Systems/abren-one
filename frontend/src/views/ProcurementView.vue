<script setup lang="ts">
import { computed, ref } from "vue";
import { useProcurement } from "@/composables/useProcurement";
import RequisitionsTab from "@/components/procurement/tabs/RequisitionsTab.vue";
import PurchaseOrdersTab from "@/components/procurement/tabs/PurchaseOrdersTab.vue";
import GoodsReceiptsTab from "@/components/procurement/tabs/GoodsReceiptsTab.vue";
import VendorsTab from "@/components/procurement/tabs/VendorsTab.vue";
import CreateRequisitionModal from "@/components/procurement/modals/CreateRequisitionModal.vue";
import CreatePurchaseOrderModal from "@/components/procurement/modals/CreatePurchaseOrderModal.vue";
import RecordGoodsReceiptModal from "@/components/procurement/modals/RecordGoodsReceiptModal.vue";
import InspectGoodsReceiptModal from "@/components/procurement/modals/InspectGoodsReceiptModal.vue";
import CreateVendorModal from "@/components/procurement/CreateVendorModal.vue";
import type { GoodsReceiptNote, PurchaseOrder } from "@/types/procurement";

const {
  vendors,
  requisitions,
  orders,
  goodsReceipts,
  selectedRequisition,
  selectedOrder,
  selectedGrn,
  isLoading,
  errorMessage,
  successMessage,
  createVendor,
  createRequisition,
  submitRequisition,
  approveRequisition,
  createOrder,
  issueOrder,
  cancelOrder,
  createGoodsReceipt,
  inspectGoodsReceipt,
  clearMessages,
} = useProcurement();

const activeTab = ref<"requisitions" | "orders" | "receipts" | "vendors">("requisitions");

// Attention panel metrics
const pendingRequisitions = computed(() =>
  requisitions.value.filter((r) => r.authorization_status === "submitted")
);
const openOrders = computed(() =>
  orders.value.filter((o) => o.status === "issued")
);
const uninspectedReceipts = computed(() =>
  goodsReceipts.value.filter((g) => !g.is_fully_inspected)
);

// Modals
const isCreatingRequisition = ref(false);
const isCreatingOrder = ref(false);
const isRecordingReceipt = ref(false);
const orderForReceipt = ref<PurchaseOrder | null>(null);
const isInspectingReceipt = ref(false);
const isCreatingVendor = ref(false);

function onReceiveDelivery(order: PurchaseOrder) {
  orderForReceipt.value = order;
  isRecordingReceipt.value = true;
  activeTab.value = "receipts";
}

function onInspectGrn(grn: GoodsReceiptNote) {
  selectedGrn.value = grn;
  isInspectingReceipt.value = true;
}

async function handleRequisitionSubmit(payload: unknown) {
  try {
    await createRequisition(payload);
    isCreatingRequisition.value = false;
  } catch {
    // handled by composable
  }
}

async function handleOrderSubmit(payload: unknown) {
  try {
    await createOrder(payload);
    isCreatingOrder.value = false;
  } catch {
    // handled by composable
  }
}

async function handleReceiptSubmit(payload: unknown) {
  try {
    await createGoodsReceipt(payload);
    isRecordingReceipt.value = false;
  } catch {
    // handled by composable
  }
}

async function handleInspectionSubmit(payload: {
  grnId: string;
  inspections: Array<{
    grn_item_id: string;
    quantity_accepted: number;
    quantity_rejected: number;
    rejection_reason?: string;
  }>;
}) {
  try {
    await inspectGoodsReceipt(payload.grnId, { inspections: payload.inspections });
    isInspectingReceipt.value = false;
  } catch {
    // handled by composable
  }
}

async function handleVendorSubmit(payload: unknown) {
  try {
    await createVendor(payload);
    isCreatingVendor.value = false;
  } catch {
    // handled by composable
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
          Commercial spend controls, supplier orders, and verified three-way goods receipt.
        </p>
      </div>
      <div class="header-actions">
        <button
          class="btn btn-primary"
          @click="
            activeTab === 'requisitions'
              ? (isCreatingRequisition = true)
              : activeTab === 'orders'
              ? (isCreatingOrder = true)
              : activeTab === 'vendors'
              ? (isCreatingVendor = true)
              : (activeTab = 'requisitions')
          "
        >
          {{
            activeTab === "requisitions"
              ? "+ Raise Requisition"
              : activeTab === "orders"
              ? "+ Issue PO"
              : activeTab === "vendors"
              ? "+ Register Vendor"
              : "+ Raise Requisition"
          }}
        </button>
      </div>
    </header>

    <!-- Notification Alerts -->
    <div v-if="errorMessage" class="alert alert-error">
      <span>⚠️</span>
      <div>{{ errorMessage }}</div>
      <button class="close-btn" @click="clearMessages">✕</button>
    </div>
    <div v-if="successMessage" class="alert alert-success">
      <span>✅</span>
      <div>{{ successMessage }}</div>
      <button class="close-btn" @click="clearMessages">✕</button>
    </div>

    <!-- Attention Panel -->
    <section class="attention-panel" aria-label="Actionable Metrics">
      <div
        class="stat-card"
        :class="{ 'stat-urgent': pendingRequisitions.length > 0 }"
        @click="activeTab = 'requisitions'"
      >
        <div class="stat-number">{{ pendingRequisitions.length }}</div>
        <div class="stat-meta">
          <div class="stat-title">Requisitions Awaiting Approval</div>
          <div class="stat-desc">Click to review authorization pipeline</div>
        </div>
      </div>
      <div
        class="stat-card"
        :class="{ 'stat-active': openOrders.length > 0 }"
        @click="activeTab = 'orders'"
      >
        <div class="stat-number">{{ openOrders.length }}</div>
        <div class="stat-meta">
          <div class="stat-title">Open Purchase Orders</div>
          <div class="stat-desc">Issued to vendors, awaiting delivery</div>
        </div>
      </div>
      <div
        class="stat-card"
        :class="{ 'stat-warning': uninspectedReceipts.length > 0 }"
        @click="activeTab = 'receipts'"
      >
        <div class="stat-number">{{ uninspectedReceipts.length }}</div>
        <div class="stat-meta">
          <div class="stat-title">Deliveries Needing Inspection</div>
          <div class="stat-desc">GRNs pending physical verification</div>
        </div>
      </div>
      <div class="stat-card" @click="activeTab = 'vendors'">
        <div class="stat-number">{{ vendors.length }}</div>
        <div class="stat-meta">
          <div class="stat-title">Active Suppliers</div>
          <div class="stat-desc">Directory of verified commercial partners</div>
        </div>
      </div>
    </section>

    <!-- Navigation Tabs -->
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
        Purchasing & Orders ({{ orders.length }})
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

    <!-- Tab Panels -->
    <RequisitionsTab
      v-if="activeTab === 'requisitions'"
      :requisitions="requisitions"
      :selected-requisition="selectedRequisition"
      :selected-fulfillment="null"
      @create-requisition="isCreatingRequisition = true"
      @view-requisition="() => {}"
      @submit-requisition="submitRequisition"
      @approve-requisition="approveRequisition"
      @close-detail="selectedRequisition = null"
    />

    <PurchaseOrdersTab
      v-else-if="activeTab === 'orders'"
      :purchase-orders="orders"
      :selected-order="selectedOrder"
      @create-order="isCreatingOrder = true"
      @view-order="() => {}"
      @issue-order="issueOrder"
      @receive-delivery="onReceiveDelivery"
      @close-order="cancelOrder($event, 'Closed by user')"
      @close-detail="selectedOrder = null"
    />

    <GoodsReceiptsTab
      v-else-if="activeTab === 'receipts'"
      :goods-receipts="goodsReceipts"
      @inspect-grn="onInspectGrn"
    />

    <VendorsTab
      v-else-if="activeTab === 'vendors'"
      :vendors="vendors"
      @create-vendor="isCreatingVendor = true"
    />

    <!-- Modals -->
    <CreateRequisitionModal
      :show="isCreatingRequisition"
      :is-loading="isLoading"
      @close="isCreatingRequisition = false"
      @submit="handleRequisitionSubmit"
    />

    <CreatePurchaseOrderModal
      :show="isCreatingOrder"
      :vendors="vendors"
      :requisitions="requisitions"
      :is-loading="isLoading"
      @close="isCreatingOrder = false"
      @submit="handleOrderSubmit"
    />

    <RecordGoodsReceiptModal
      :show="isRecordingReceipt"
      :order="orderForReceipt"
      :is-loading="isLoading"
      @close="isRecordingReceipt = false"
      @submit="handleReceiptSubmit"
    />

    <InspectGoodsReceiptModal
      :show="isInspectingReceipt"
      :grn="selectedGrn"
      :is-loading="isLoading"
      @close="isInspectingReceipt = false"
      @submit="handleInspectionSubmit"
    />

    <CreateVendorModal
      :show="isCreatingVendor"
      :is-loading="isLoading"
      @close="isCreatingVendor = false"
      @submit="handleVendorSubmit"
    />
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
  color: var(--color-text);
  margin: 0 0 0.25rem 0;
}

.page-subtitle {
  color: var(--color-text-muted);
  font-size: 0.9375rem;
  margin: 0;
}

.attention-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  color: var(--color-text);
}

.stat-title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--color-text);
}

.stat-desc {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.stat-urgent {
  border-left: 4px solid #ef4444;
}

.stat-urgent .stat-number {
  color: #ef4444;
}

.stat-active {
  border-left: 4px solid var(--color-primary);
}

.stat-active .stat-number {
  color: var(--color-primary);
}

.stat-warning {
  border-left: 4px solid #f59e0b;
}

.stat-warning .stat-number {
  color: #f59e0b;
}

.tabs-nav {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tab-btn {
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 0.75rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
}

.alert-error {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-success {
  background-color: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.close-btn {
  margin-left: auto;
  background: transparent;
  border: none;
  cursor: pointer;
  color: inherit;
  font-size: 1rem;
}
</style>
