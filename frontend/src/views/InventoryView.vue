<script setup lang="ts">
import { ref } from "vue";
import { useInventory } from "@/composables/useInventory";
import StockBalancesTab from "@/components/inventory/tabs/StockBalancesTab.vue";
import StockMovementsTab from "@/components/inventory/tabs/StockMovementsTab.vue";
import ItemsCatalogTab from "@/components/inventory/tabs/ItemsCatalogTab.vue";
import WarehousesTab from "@/components/inventory/tabs/WarehousesTab.vue";
import CreateItemModal from "@/components/inventory/modals/CreateItemModal.vue";
import CreateCategoryModal from "@/components/inventory/modals/CreateCategoryModal.vue";
import CreateWarehouseModal from "@/components/inventory/modals/CreateWarehouseModal.vue";
import AddBatchModal from "@/components/inventory/modals/AddBatchModal.vue";
import AddLocationModal from "@/components/inventory/modals/AddLocationModal.vue";
import StockMovementModal, {
  type MovementType,
} from "@/components/inventory/modals/StockMovementModal.vue";
import ReceivePurchaseModal from "@/components/inventory/ReceivePurchaseModal.vue";
import TransactionDetailModal from "@/components/inventory/TransactionDetailModal.vue";

const {
  categories,
  items,
  warehouses,
  balances,
  ledgerEntries,
  reorderAlerts,
  expiringBatches,
  pendingGrns,
  selectedTransaction,
  isLoading,
  errorMessage,
  successMessage,
  loadPendingGrns,
  fetchTransactionDetail,
  createCategory,
  createItem,
  createBatch,
  createWarehouse,
  createLocation,
  recordMovement,
  intakeGrn,
  runReconciliation,
  clearMessages,
} = useInventory();

const activeTab = ref<"balances" | "movements" | "items" | "warehouses">("balances");

// Modal visibility flags
const showCreateItemModal = ref(false);
const showCreateCategoryModal = ref(false);
const showCreateWarehouseModal = ref(false);
const showAddBatchModal = ref(false);
const selectedBatchItemId = ref("");
const showAddLocationModal = ref(false);
const selectedWarehouseId = ref("");
const showReceivePurchaseModal = ref(false);
const showTransactionDetailModal = ref(false);

// Movement modal
const showMovementModal = ref(false);
const activeMovementType = ref<MovementType>("opening");

function openMovement(type: MovementType) {
  activeMovementType.value = type;
  showMovementModal.value = true;
}

async function handleViewTransaction(id: string) {
  await fetchTransactionDetail(id);
  showTransactionDetailModal.value = true;
}

async function handleReceivePurchaseSubmit(payload: unknown) {
  try {
    await intakeGrn(payload);
    showReceivePurchaseModal.value = false;
  } catch {
    // Error state managed by composable
  }
}

async function handleMovementSubmit(payload: {
  endpoint: string;
  data: Record<string, unknown>;
}) {
  try {
    await recordMovement(payload.endpoint, payload.data);
    showMovementModal.value = false;
  } catch {
    // Error state managed by composable
  }
}

function onAddBatch(itemId: string) {
  selectedBatchItemId.value = itemId;
  showAddBatchModal.value = true;
}

function onAddLocation(warehouseId: string) {
  selectedWarehouseId.value = warehouseId;
  showAddLocationModal.value = true;
}

async function openReceivePurchase() {
  await loadPendingGrns();
  showReceivePurchaseModal.value = true;
}
</script>

<template>
  <div class="inventory-view">
    <!-- Header -->
    <header class="view-header">
      <div class="header-content">
        <h1>Inventory & Stock Management</h1>
        <p class="subtitle">
          Item master catalog, storage facilities, and immutable stock ledger.
        </p>
      </div>
      <div class="header-actions">
        <button
          class="btn btn-secondary"
          :disabled="isLoading"
          @click="runReconciliation"
        >
          <span>⚖️</span> Reconcile Ledger
        </button>
        <button class="btn btn-secondary" @click="openReceivePurchase">
          <span>📦</span> Receive Purchase (GRN)
        </button>
        <button class="btn btn-primary" @click="openMovement('opening')">
          <span>📥</span> Opening Stock
        </button>
      </div>
    </header>

    <!-- Alerts -->
    <div v-if="errorMessage" class="alert alert-error" role="alert">
      <span>⚠️</span>
      <div>{{ errorMessage }}</div>
      <button class="close-btn" @click="clearMessages">✕</button>
    </div>
    <div v-if="successMessage" class="alert alert-success" role="alert">
      <span>✅</span>
      <div>{{ successMessage }}</div>
      <button class="close-btn" @click="clearMessages">✕</button>
    </div>

    <!-- Attention Panel -->
    <section class="attention-panel" aria-label="Inventory Overview">
      <div class="stat-card" :class="{ warning: reorderAlerts.length > 0 }">
        <div class="stat-icon">📉</div>
        <div class="stat-details">
          <div class="stat-value">{{ reorderAlerts.length }}</div>
          <div class="stat-label">Reorder Threshold Alerts</div>
        </div>
      </div>
      <div class="stat-card" :class="{ danger: expiringBatches.length > 0 }">
        <div class="stat-icon">⏳</div>
        <div class="stat-details">
          <div class="stat-value">{{ expiringBatches.length }}</div>
          <div class="stat-label">Batches Expiring Soon (90d)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <div class="stat-details">
          <div class="stat-value">{{ warehouses.length }}</div>
          <div class="stat-label">Warehouses Active</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-details">
          <div class="stat-value">{{ items.length }}</div>
          <div class="stat-label">Cataloged Items</div>
        </div>
      </div>
    </section>

    <!-- Tabs Navigation -->
    <nav class="tabs-nav" aria-label="Inventory Tabs">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'balances' }"
        @click="activeTab = 'balances'"
      >
        <span>📊</span> Stock Balances
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'movements' }"
        @click="activeTab = 'movements'"
      >
        <span>📑</span> Stock Movements
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'items' }"
        @click="activeTab = 'items'"
      >
        <span>🏷️</span> Items & Categories
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'warehouses' }"
        @click="activeTab = 'warehouses'"
      >
        <span>🏬</span> Warehouses & Locations
      </button>
    </nav>

    <!-- Tab Panels -->
    <StockBalancesTab
      v-if="activeTab === 'balances'"
      :balances="balances"
      :warehouses="warehouses"
    />

    <StockMovementsTab
      v-else-if="activeTab === 'movements'"
      :ledger-entries="ledgerEntries"
      :warehouses="warehouses"
      @view-transaction="handleViewTransaction"
      @open-receive-purchase="openReceivePurchase"
      @open-donation="openMovement('donation')"
      @open-transfer="openMovement('transfer')"
      @open-issue="openMovement('issue')"
      @open-adjust="openMovement('adjust')"
      @open-write-off="openMovement('write_off')"
    />

    <ItemsCatalogTab
      v-else-if="activeTab === 'items'"
      :items="items"
      :categories="categories"
      @create-item="showCreateItemModal = true"
      @create-category="showCreateCategoryModal = true"
      @add-batch="onAddBatch"
      @view-item="() => {}"
    />

    <WarehousesTab
      v-else-if="activeTab === 'warehouses'"
      :warehouses="warehouses"
      @create-warehouse="showCreateWarehouseModal = true"
      @add-location="onAddLocation"
      @view-warehouse="() => {}"
    />

    <!-- Modals -->
    <CreateItemModal
      :show="showCreateItemModal"
      :categories="categories"
      :is-loading="isLoading"
      @close="showCreateItemModal = false"
      @submit="(data) => createItem(data).then(() => (showCreateItemModal = false))"
    />

    <CreateCategoryModal
      :show="showCreateCategoryModal"
      :categories="categories"
      :is-loading="isLoading"
      @close="showCreateCategoryModal = false"
      @submit="(data) => createCategory(data).then(() => (showCreateCategoryModal = false))"
    />

    <CreateWarehouseModal
      :show="showCreateWarehouseModal"
      :is-loading="isLoading"
      @close="showCreateWarehouseModal = false"
      @submit="(data) => createWarehouse(data).then(() => (showCreateWarehouseModal = false))"
    />

    <AddBatchModal
      :show="showAddBatchModal"
      :item-id="selectedBatchItemId"
      :is-loading="isLoading"
      @close="showAddBatchModal = false"
      @submit="(data) => createBatch(data.itemId, data).then(() => (showAddBatchModal = false))"
    />

    <AddLocationModal
      :show="showAddLocationModal"
      :warehouse-id="selectedWarehouseId"
      :is-loading="isLoading"
      @close="showAddLocationModal = false"
      @submit="(data) => createLocation(data.warehouseId, data).then(() => (showAddLocationModal = false))"
    />

    <StockMovementModal
      :show="showMovementModal"
      :type="activeMovementType"
      :warehouses="warehouses"
      :items="items"
      :is-loading="isLoading"
      @close="showMovementModal = false"
      @submit="handleMovementSubmit"
    />

    <ReceivePurchaseModal
      :show="showReceivePurchaseModal"
      :pending-grns="pendingGrns"
      :warehouses="warehouses"
      :items="items"
      :is-loading="isLoading"
      @close="showReceivePurchaseModal = false"
      @submit="handleReceivePurchaseSubmit"
    />

    <TransactionDetailModal
      :show="showTransactionDetailModal"
      :transaction="selectedTransaction"
      @close="showTransactionDetailModal = false"
    />
  </div>
</template>

<style scoped>
.inventory-view {
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subtitle {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.attention-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-card.warning {
  border-left: 4px solid #f59e0b;
}

.stat-card.danger {
  border-left: 4px solid #ef4444;
}

.stat-icon {
  font-size: 1.75rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.tabs-nav {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  gap: 0.5rem;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  border-radius: var(--radius-md);
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
