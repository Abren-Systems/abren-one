<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { api } from "@/api/client";
import { useTenantStore } from "@/stores/tenant";
import type {
  ExpiringBatchAlert,
  ItemCategory,
  ItemDetail,
  ItemSummary,
  ReconciliationReport,
  ReorderAlert,
  StockBalance,
  StockLedgerEntry,
  TransactionDetail,
  WarehouseDetail,
  WarehouseSummary,
} from "@/types/inventory";

const tenantStore = useTenantStore();

const activeTab = ref<"items" | "warehouses" | "balances" | "movements">("balances");
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);

// ── Master Data Lists ──
const categories = ref<ItemCategory[]>([]);
const items = ref<ItemSummary[]>([]);
const warehouses = ref<WarehouseSummary[]>([]);
const balances = ref<StockBalance[]>([]);
const ledgerEntries = ref<StockLedgerEntry[]>([]);
const reorderAlerts = ref<ReorderAlert[]>([]);
const expiringBatches = ref<ExpiringBatchAlert[]>([]);
const reconciliationReport = ref<ReconciliationReport | null>(null);

// ── Selection State ──
const selectedItem = ref<ItemDetail | null>(null);
const selectedWarehouse = ref<WarehouseDetail | null>(null);
const selectedTransaction = ref<TransactionDetail | null>(null);

// ── Modals Visibility ──
const showCreateItemModal = ref(false);
const showCreateCategoryModal = ref(false);
const showAddBatchModal = ref(false);
const showCreateWarehouseModal = ref(false);
const showAddLocationModal = ref(false);
const showOpeningStockModal = ref(false);
const showDonationModal = ref(false);
const showTransferModal = ref(false);
const showIssueModal = ref(false);
const showAdjustModal = ref(false);
const showWriteOffModal = ref(false);
const showTransactionDetailModal = ref(false);

// ── Filter State ──
const itemSearch = ref("");
const itemCategoryFilter = ref("");
const balanceWarehouseFilter = ref("");
const balanceLowStockOnly = ref(false);
const ledgerWarehouseFilter = ref("");

// ── Form Models ──
// Item Form
const newItem = ref({
  category_id: "",
  item_code: "",
  name: "",
  description: "",
  unit_of_measure: "each",
  item_type: "consumable",
  track_batches: false,
  track_expiry: false,
  reorder_threshold: "0.00",
  default_unit_cost: "0.00",
});

// Category Form
const newCategory = ref({
  name: "",
  code: "",
  description: "",
  parent_id: "" as string | null,
});

// Batch Form
const newBatch = ref({
  item_id: "",
  batch_number: "",
  manufacture_date: "",
  expiry_date: "",
});

// Warehouse Form
const newWarehouse = ref({
  name: "",
  code: "",
  warehouse_type: "regional_depot",
  address: "",
});

// Location Form
const newLocation = ref({
  warehouse_id: "",
  name: "",
  code: "",
});

// Opening Stock Form
const openingStockForm = ref({
  warehouse_id: "",
  transaction_date: new Date().toISOString().split("T")[0],
  reference_document: "",
  notes: "",
  lines: [{ item_id: "", quantity: 1, unit_cost: 0, batch_id: "" }],
});

// Donation Form
const donationForm = ref({
  warehouse_id: "",
  donor_name: "",
  transaction_date: new Date().toISOString().split("T")[0],
  reference_document: "",
  notes: "",
  lines: [{ item_id: "", quantity: 1, unit_cost: 0, batch_id: "" }],
});

// Transfer Form
const transferForm = ref({
  source_warehouse_id: "",
  destination_warehouse_id: "",
  transaction_date: new Date().toISOString().split("T")[0],
  reference_document: "",
  notes: "",
  lines: [{ item_id: "", quantity: 1, batch_id: "" }],
});

// Issue Form
const issueForm = ref({
  warehouse_id: "",
  transaction_date: new Date().toISOString().split("T")[0],
  is_program_issue: false,
  recipient_name: "",
  reference_document: "",
  notes: "",
  lines: [{ item_id: "", quantity: 1, batch_id: "" }],
});

// Adjust Form
const adjustForm = ref({
  warehouse_id: "",
  transaction_date: new Date().toISOString().split("T")[0],
  justification: "",
  reference_document: "",
  lines: [{ item_id: "", actual_quantity_counted: 0, batch_id: "", reason: "" }],
});

// Write Off Form
const writeOffForm = ref({
  warehouse_id: "",
  transaction_date: new Date().toISOString().split("T")[0],
  approval_reference: "",
  justification: "",
  lines: [{ item_id: "", quantity: 1, reason: "damaged", batch_id: "" }],
});

// ── Computed Properties ──
const filteredItems = computed(() => {
  return items.value.filter((i) => {
    const matchesSearch =
      !itemSearch.value ||
      i.name.toLowerCase().includes(itemSearch.value.toLowerCase()) ||
      i.item_code.toLowerCase().includes(itemSearch.value.toLowerCase());
    const matchesCat =
      !itemCategoryFilter.value || i.category_id === itemCategoryFilter.value;
    return matchesSearch && matchesCat;
  });
});

const filteredBalances = computed(() => {
  return balances.value.filter((b) => {
    const matchesWh =
      !balanceWarehouseFilter.value || b.warehouse_id === balanceWarehouseFilter.value;
    const matchesLow = !balanceLowStockOnly.value || b.is_low_stock;
    return matchesWh && matchesLow;
  });
});

const filteredLedger = computed(() => {
  return ledgerEntries.value.filter((e) => {
    return (
      !ledgerWarehouseFilter.value || e.warehouse_id === ledgerWarehouseFilter.value
    );
  });
});

// ── Fetch Operations ──
async function loadData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  errorMessage.value = null;

  try {
    const [
      catRes,
      itemRes,
      whRes,
      balRes,
      ledgerRes,
      alertsRes,
    ] = await Promise.all([
      api.get<ItemCategory[]>("/api/v1/inventory/categories/"),
      api.get<ItemSummary[]>("/api/v1/inventory/items/"),
      api.get<WarehouseSummary[]>("/api/v1/inventory/warehouses/"),
      api.get<StockBalance[]>("/api/v1/inventory/balances/"),
      api.get<StockLedgerEntry[]>("/api/v1/inventory/ledger/"),
      api.get<{ reorder_alerts: ReorderAlert[]; expiring_batches: ExpiringBatchAlert[] }>(
        "/api/v1/inventory/alerts/"
      ),
    ]);

    categories.value = catRes;
    items.value = itemRes;
    warehouses.value = whRes;
    balances.value = balRes;
    ledgerEntries.value = ledgerRes;
    reorderAlerts.value = alertsRes.reorder_alerts;
    expiringBatches.value = alertsRes.expiring_batches;
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to load inventory data.";
  } finally {
    isLoading.value = false;
  }
}

async function runReconciliation() {
  isLoading.value = true;
  try {
    const res = await api.get<ReconciliationReport>("/api/v1/inventory/balances/reconciliation/");
    reconciliationReport.value = res;
    if (res.is_healthy) {
      successMessage.value = `Audit complete: All ${res.total_balances_checked} stock balances match the immutable ledger exactly.`;
    } else {
      errorMessage.value = `Audit warning: ${res.discrepancies_count} balance discrepancies detected.`;
    }
  } catch (err: any) {
    errorMessage.value = err.message || "Reconciliation failed.";
  } finally {
    isLoading.value = false;
  }
}

async function viewItemDetail(id: string) {
  try {
    selectedItem.value = await api.get<ItemDetail>(`/api/v1/inventory/items/${id}/`);
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to fetch item detail.";
  }
}

async function viewWarehouseDetail(id: string) {
  try {
    selectedWarehouse.value = await api.get<WarehouseDetail>(`/api/v1/inventory/warehouses/${id}/`);
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to fetch warehouse detail.";
  }
}

async function viewTransaction(id: string) {
  try {
    selectedTransaction.value = await api.get<TransactionDetail>(`/api/v1/inventory/transactions/${id}/`);
    showTransactionDetailModal.value = true;
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to fetch transaction detail.";
  }
}

// ── Submit Handlers ──
async function submitCategory() {
  if (!newCategory.value.name.trim() || !newCategory.value.code.trim()) return;
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/categories/", {
      name: newCategory.value.name.trim(),
      code: newCategory.value.code.trim(),
      description: newCategory.value.description.trim(),
      parent_id: newCategory.value.parent_id || null,
    });
    showCreateCategoryModal.value = false;
    newCategory.value = { name: "", code: "", description: "", parent_id: null };
    successMessage.value = "Category created successfully.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to create category.";
  } finally {
    isLoading.value = false;
  }
}

async function submitItem() {
  if (!newItem.value.name.trim() || !newItem.value.item_code.trim()) return;
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/items/", {
      ...newItem.value,
      reorder_threshold: newItem.value.reorder_threshold || "0.00",
      default_unit_cost: newItem.value.default_unit_cost || "0.00",
    });
    showCreateItemModal.value = false;
    newItem.value = {
      category_id: "",
      item_code: "",
      name: "",
      description: "",
      unit_of_measure: "each",
      item_type: "consumable",
      track_batches: false,
      track_expiry: false,
      reorder_threshold: "0.00",
      default_unit_cost: "0.00",
    };
    successMessage.value = "Item created successfully.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to create item.";
  } finally {
    isLoading.value = false;
  }
}

async function submitBatch() {
  if (!newBatch.value.item_id || !newBatch.value.batch_number.trim()) return;
  isLoading.value = true;
  try {
    await api.post(`/api/v1/inventory/items/${newBatch.value.item_id}/batches/`, {
      batch_number: newBatch.value.batch_number.trim(),
      manufacture_date: newBatch.value.manufacture_date || null,
      expiry_date: newBatch.value.expiry_date || null,
    });
    showAddBatchModal.value = false;
    newBatch.value = { item_id: "", batch_number: "", manufacture_date: "", expiry_date: "" };
    successMessage.value = "Batch registered successfully.";
    await loadData();
    if (selectedItem.value) {
      await viewItemDetail(selectedItem.value.id);
    }
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to add batch.";
  } finally {
    isLoading.value = false;
  }
}

async function submitWarehouse() {
  if (!newWarehouse.value.name.trim() || !newWarehouse.value.code.trim()) return;
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/warehouses/", {
      ...newWarehouse.value,
    });
    showCreateWarehouseModal.value = false;
    newWarehouse.value = { name: "", code: "", warehouse_type: "regional_depot", address: "" };
    successMessage.value = "Warehouse created successfully.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to create warehouse.";
  } finally {
    isLoading.value = false;
  }
}

async function submitLocation() {
  if (!newLocation.value.warehouse_id || !newLocation.value.code.trim()) return;
  isLoading.value = true;
  try {
    await api.post(`/api/v1/inventory/warehouses/${newLocation.value.warehouse_id}/locations/`, {
      name: newLocation.value.name.trim(),
      code: newLocation.value.code.trim(),
    });
    showAddLocationModal.value = false;
    newLocation.value = { warehouse_id: "", name: "", code: "" };
    successMessage.value = "Storage location added.";
    await loadData();
    if (selectedWarehouse.value) {
      await viewWarehouseDetail(selectedWarehouse.value.id);
    }
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to add storage location.";
  } finally {
    isLoading.value = false;
  }
}

async function submitOpeningStock() {
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/transactions/receipt-opening/", {
      warehouse_id: openingStockForm.value.warehouse_id,
      transaction_date: openingStockForm.value.transaction_date,
      reference_document: openingStockForm.value.reference_document,
      notes: openingStockForm.value.notes,
      lines: openingStockForm.value.lines.map((l) => ({
        item_id: l.item_id,
        quantity: l.quantity,
        unit_cost: l.unit_cost,
        batch_id: l.batch_id || null,
      })),
    });
    showOpeningStockModal.value = false;
    successMessage.value = "Opening stock posted to ledger.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to post opening stock.";
  } finally {
    isLoading.value = false;
  }
}

async function submitDonation() {
  if (!donationForm.value.donor_name.trim()) return;
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/transactions/receipt-donation/", {
      warehouse_id: donationForm.value.warehouse_id,
      donor_name: donationForm.value.donor_name.trim(),
      transaction_date: donationForm.value.transaction_date,
      reference_document: donationForm.value.reference_document,
      notes: donationForm.value.notes,
      lines: donationForm.value.lines.map((l) => ({
        item_id: l.item_id,
        quantity: l.quantity,
        unit_cost: l.unit_cost,
        batch_id: l.batch_id || null,
      })),
    });
    showDonationModal.value = false;
    successMessage.value = "In-kind donation receipt posted to ledger.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to post donation receipt.";
  } finally {
    isLoading.value = false;
  }
}

async function submitTransfer() {
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/transactions/transfer/", {
      source_warehouse_id: transferForm.value.source_warehouse_id,
      destination_warehouse_id: transferForm.value.destination_warehouse_id,
      transaction_date: transferForm.value.transaction_date,
      reference_document: transferForm.value.reference_document,
      notes: transferForm.value.notes,
      lines: transferForm.value.lines.map((l) => ({
        item_id: l.item_id,
        quantity: l.quantity,
        batch_id: l.batch_id || null,
      })),
    });
    showTransferModal.value = false;
    successMessage.value = "Inter-warehouse transfer executed atomically.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Transfer failed.";
  } finally {
    isLoading.value = false;
  }
}

async function submitIssue() {
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/transactions/issue/", {
      warehouse_id: issueForm.value.warehouse_id,
      transaction_date: issueForm.value.transaction_date,
      is_program_issue: issueForm.value.is_program_issue,
      recipient_name: issueForm.value.recipient_name,
      reference_document: issueForm.value.reference_document,
      notes: issueForm.value.notes,
      lines: issueForm.value.lines.map((l) => ({
        item_id: l.item_id,
        quantity: l.quantity,
        batch_id: l.batch_id || null,
      })),
    });
    showIssueModal.value = false;
    successMessage.value = "Supplies successfully issued and deducted from inventory.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Stock issue failed.";
  } finally {
    isLoading.value = false;
  }
}

async function submitAdjust() {
  if (!adjustForm.value.justification.trim()) return;
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/transactions/adjust/", {
      warehouse_id: adjustForm.value.warehouse_id,
      transaction_date: adjustForm.value.transaction_date,
      justification: adjustForm.value.justification.trim(),
      reference_document: adjustForm.value.reference_document,
      lines: adjustForm.value.lines.map((l) => ({
        item_id: l.item_id,
        actual_quantity_counted: l.actual_quantity_counted,
        batch_id: l.batch_id || null,
        reason: l.reason,
      })),
    });
    showAdjustModal.value = false;
    successMessage.value = "Physical cycle count discrepancy reconciled.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Count adjustment failed.";
  } finally {
    isLoading.value = false;
  }
}

async function submitWriteOff() {
  if (!writeOffForm.value.approval_reference.trim() || !writeOffForm.value.justification.trim()) return;
  isLoading.value = true;
  try {
    await api.post("/api/v1/inventory/transactions/write-off/", {
      warehouse_id: writeOffForm.value.warehouse_id,
      transaction_date: writeOffForm.value.transaction_date,
      approval_reference: writeOffForm.value.approval_reference.trim(),
      justification: writeOffForm.value.justification.trim(),
      lines: writeOffForm.value.lines.map((l) => ({
        item_id: l.item_id,
        quantity: l.quantity,
        reason: l.reason,
        batch_id: l.batch_id || null,
      })),
    });
    showWriteOffModal.value = false;
    successMessage.value = "Authorized stock write-off recorded in ledger.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Write-off failed.";
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
        <button class="btn btn-secondary" :disabled="isLoading" @click="runReconciliation">
          <span>⚖️</span> Reconcile Ledger
        </button>
        <button class="btn btn-primary" @click="showOpeningStockModal = true">
          <span>📥</span> Opening Stock
        </button>
      </div>
    </header>

    <!-- Alerts -->
    <div v-if="errorMessage" class="alert alert-error" role="alert">
      <span>⚠️</span>
      <div>{{ errorMessage }}</div>
      <button class="close-btn" @click="errorMessage = null">✕</button>
    </div>
    <div v-if="successMessage" class="alert alert-success" role="alert">
      <span>✅</span>
      <div>{{ successMessage }}</div>
      <button class="close-btn" @click="successMessage = null">✕</button>
    </div>

    <!-- Attention Panel -->
    <section class="attention-panel" aria-label="Inventory Alerts">
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
        <span>📑</span> Stock Movements (Ledger)
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

    <!-- TAB 1: Stock Balances -->
    <div v-if="activeTab === 'balances'" class="tab-content">
      <div class="toolbar">
        <div class="filter-group">
          <select v-model="balanceWarehouseFilter" class="form-select">
            <option value="">All Warehouses</option>
            <option v-for="w in warehouses" :key="w.id" :value="w.id">
              {{ w.name }} ({{ w.code }})
            </option>
          </select>
          <label class="checkbox-label">
            <input v-model="balanceLowStockOnly" type="checkbox" />
            <span>Low Stock Alerts Only</span>
          </label>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Item Code</th>
              <th>Item Name</th>
              <th>Warehouse</th>
              <th>Location</th>
              <th>Batch / Lot</th>
              <th>Expiry</th>
              <th class="text-right">On Hand</th>
              <th class="text-right">Reserved</th>
              <th class="text-right">Available</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredBalances.length === 0">
              <td colspan="10" class="empty-state">No stock balances found.</td>
            </tr>
            <tr v-for="b in filteredBalances" :key="b.id">
              <td class="code-cell font-mono">{{ b.item_code }}</td>
              <td>{{ b.item_name }}</td>
              <td>{{ b.warehouse_name }}</td>
              <td>{{ b.location_code || '—' }}</td>
              <td>{{ b.batch_number || '—' }}</td>
              <td>{{ b.expiry_date || '—' }}</td>
              <td class="text-right font-mono">{{ b.quantity_on_hand }} {{ b.unit_of_measure }}</td>
              <td class="text-right font-mono">{{ b.quantity_reserved }}</td>
              <td class="text-right font-mono font-bold">{{ b.available_quantity }}</td>
              <td>
                <span v-if="b.is_low_stock" class="badge badge-warning">Low Stock</span>
                <span v-else class="badge badge-success">Adequate</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 2: Stock Movements (Ledger) -->
    <div v-if="activeTab === 'movements'" class="tab-content">
      <div class="toolbar">
        <div class="filter-group">
          <select v-model="ledgerWarehouseFilter" class="form-select">
            <option value="">All Warehouses</option>
            <option v-for="w in warehouses" :key="w.id" :value="w.id">
              {{ w.name }} ({{ w.code }})
            </option>
          </select>
        </div>
        <div class="action-button-group">
          <button class="btn btn-secondary btn-sm" @click="showDonationModal = true">
            <span>🎁</span> In-Kind Donation
          </button>
          <button class="btn btn-secondary btn-sm" @click="showTransferModal = true">
            <span>🔄</span> Transfer Stock
          </button>
          <button class="btn btn-secondary btn-sm" @click="showIssueModal = true">
            <span>📤</span> Issue Supplies
          </button>
          <button class="btn btn-secondary btn-sm" @click="showAdjustModal = true">
            <span>⚖️</span> Count Adjust
          </button>
          <button class="btn btn-secondary btn-sm" @click="showWriteOffModal = true">
            <span>🗑️</span> Write-Off
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Txn Number</th>
              <th>Type</th>
              <th>Warehouse</th>
              <th>Item</th>
              <th>Batch</th>
              <th class="text-right">Quantity</th>
              <th class="text-right">Unit Cost</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredLedger.length === 0">
              <td colspan="9" class="empty-state">No stock ledger movements posted.</td>
            </tr>
            <tr v-for="e in filteredLedger" :key="e.id">
              <td>{{ e.transaction_date }}</td>
              <td class="font-mono">
                <a href="#" class="txn-link" @click.prevent="viewTransaction(e.transaction_id)">
                  {{ e.transaction_number }}
                </a>
              </td>
              <td>
                <span class="badge" :class="'badge-' + e.transaction_type">
                  {{ e.transaction_type.replace('_', ' ') }}
                </span>
              </td>
              <td>{{ e.warehouse_code }}</td>
              <td>{{ e.item_name }}</td>
              <td>{{ e.batch_number || '—' }}</td>
              <td class="text-right font-mono" :class="Number(e.quantity) >= 0 ? 'text-positive' : 'text-negative'">
                {{ Number(e.quantity) >= 0 ? '+' : '' }}{{ e.quantity }} {{ e.unit_of_measure }}
              </td>
              <td class="text-right font-mono">${{ e.unit_cost }}</td>
              <td>
                <button class="btn btn-ghost btn-xs" @click="viewTransaction(e.transaction_id)">
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 3: Items & Categories -->
    <div v-if="activeTab === 'items'" class="tab-content">
      <div class="toolbar">
        <div class="filter-group">
          <input
            v-model="itemSearch"
            type="text"
            placeholder="Search items by code or name..."
            class="form-input"
          />
          <select v-model="itemCategoryFilter" class="form-select">
            <option value="">All Categories</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>
        <div class="action-button-group">
          <button class="btn btn-secondary btn-sm" @click="showCreateCategoryModal = true">
            + Category
          </button>
          <button class="btn btn-primary btn-sm" @click="showCreateItemModal = true">
            + New Item
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Item Code</th>
              <th>Name</th>
              <th>Category</th>
              <th>UOM</th>
              <th>Type</th>
              <th>Batch / Expiry</th>
              <th class="text-right">Reorder Threshold</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredItems.length === 0">
              <td colspan="9" class="empty-state">No cataloged items found.</td>
            </tr>
            <tr v-for="item in filteredItems" :key="item.id">
              <td class="font-mono font-bold">{{ item.item_code }}</td>
              <td>{{ item.name }}</td>
              <td>{{ item.category_name }}</td>
              <td>{{ item.unit_of_measure }}</td>
              <td><span class="tag">{{ item.item_type }}</span></td>
              <td>
                <span v-if="item.track_batches" class="tag tag-blue">Batches</span>
                <span v-if="item.track_expiry" class="tag tag-amber">Expiry</span>
                <span v-if="!item.track_batches && !item.track_expiry">—</span>
              </td>
              <td class="text-right font-mono">{{ item.reorder_threshold }}</td>
              <td>
                <span class="badge" :class="item.is_active ? 'badge-success' : 'badge-muted'">
                  {{ item.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <button
                  v-if="item.track_batches"
                  class="btn btn-ghost btn-xs"
                  @click="newBatch.item_id = item.id; showAddBatchModal = true"
                >
                  + Batch
                </button>
                <button class="btn btn-ghost btn-xs" @click="viewItemDetail(item.id)">
                  Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: Warehouses & Storage Locations -->
    <div v-if="activeTab === 'warehouses'" class="tab-content">
      <div class="toolbar">
        <div></div>
        <button class="btn btn-primary btn-sm" @click="showCreateWarehouseModal = true">
          + New Warehouse
        </button>
      </div>

      <div class="warehouse-grid">
        <div v-for="wh in warehouses" :key="wh.id" class="warehouse-card">
          <div class="wh-header">
            <div>
              <h3>{{ wh.name }}</h3>
              <span class="wh-code font-mono">{{ wh.code }}</span>
            </div>
            <span class="badge" :class="wh.is_active ? 'badge-success' : 'badge-muted'">
              {{ wh.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="wh-body">
            <p><strong>Type:</strong> {{ wh.warehouse_type.replace('_', ' ') }}</p>
            <p><strong>Internal Locations:</strong> {{ wh.location_count }}</p>
          </div>
          <div class="wh-footer">
            <button
              class="btn btn-secondary btn-sm"
              @click="newLocation.warehouse_id = wh.id; showAddLocationModal = true"
            >
              + Location
            </button>
            <button class="btn btn-ghost btn-sm" @click="viewWarehouseDetail(wh.id)">
              View Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── MODALS ── -->

    <!-- Modal: Opening Stock -->
    <div v-if="showOpeningStockModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Record Opening Stock Intake</h3>
        <p class="modal-subtitle">Baseline physical inventory intake for warehouse setup.</p>
        <form @submit.prevent="submitOpeningStock">
          <div class="form-row">
            <div class="form-group">
              <label>Warehouse</label>
              <select v-model="openingStockForm.warehouse_id" required class="form-select">
                <option value="" disabled>Select warehouse</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Date</label>
              <input v-model="openingStockForm.transaction_date" type="date" required class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Reference Document</label>
            <input v-model="openingStockForm.reference_document" type="text" placeholder="e.g. AUDIT-2026-COUNT" class="form-input" />
          </div>

          <div class="lines-section">
            <h4>Item Quantities</h4>
            <div v-for="(line, idx) in openingStockForm.lines" :key="idx" class="line-row">
              <select v-model="line.item_id" required class="form-select">
                <option value="" disabled>Select Item</option>
                <option v-for="item in items" :key="item.id" :value="item.id">
                  {{ item.name }} ({{ item.item_code }})
                </option>
              </select>
              <input v-model.number="line.quantity" type="number" step="0.01" min="0.01" required placeholder="Qty" class="form-input" />
              <input v-model.number="line.unit_cost" type="number" step="0.01" min="0" placeholder="Unit Cost" class="form-input" />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showOpeningStockModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Post Opening Stock</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Inter-Warehouse Transfer -->
    <div v-if="showTransferModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Inter-Warehouse Stock Transfer</h3>
        <p class="modal-subtitle">Immediate atomic movement between facilities.</p>
        <form @submit.prevent="submitTransfer">
          <div class="form-row">
            <div class="form-group">
              <label>Source Warehouse</label>
              <select v-model="transferForm.source_warehouse_id" required class="form-select">
                <option value="" disabled>Select source</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Destination Warehouse</label>
              <select v-model="transferForm.destination_warehouse_id" required class="form-select">
                <option value="" disabled>Select destination</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Transfer Date</label>
            <input v-model="transferForm.transaction_date" type="date" required class="form-input" />
          </div>

          <div class="lines-section">
            <h4>Transfer Lines</h4>
            <div v-for="(line, idx) in transferForm.lines" :key="idx" class="line-row">
              <select v-model="line.item_id" required class="form-select">
                <option value="" disabled>Select Item</option>
                <option v-for="item in items" :key="item.id" :value="item.id">
                  {{ item.name }} ({{ item.item_code }})
                </option>
              </select>
              <input v-model.number="line.quantity" type="number" step="0.01" min="0.01" required placeholder="Qty" class="form-input" />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showTransferModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Execute Transfer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Issue Supplies -->
    <div v-if="showIssueModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Issue Stock / Supplies</h3>
        <p class="modal-subtitle">Deduct stock for organizational operations or program aid.</p>
        <form @submit.prevent="submitIssue">
          <div class="form-row">
            <div class="form-group">
              <label>Warehouse</label>
              <select v-model="issueForm.warehouse_id" required class="form-select">
                <option value="" disabled>Select warehouse</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Issue Date</label>
              <input v-model="issueForm.transaction_date" type="date" required class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Recipient / Destination Party</label>
            <input v-model="issueForm.recipient_name" type="text" placeholder="e.g. Field Team A, Clinic" class="form-input" />
          </div>

          <div class="lines-section">
            <h4>Items to Issue</h4>
            <div v-for="(line, idx) in issueForm.lines" :key="idx" class="line-row">
              <select v-model="line.item_id" required class="form-select">
                <option value="" disabled>Select Item</option>
                <option v-for="item in items" :key="item.id" :value="item.id">
                  {{ item.name }} ({{ item.item_code }})
                </option>
              </select>
              <input v-model.number="line.quantity" type="number" step="0.01" min="0.01" required placeholder="Qty" class="form-input" />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showIssueModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Issue Stock</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Cycle Count Adjust -->
    <div v-if="showAdjustModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Physical Cycle Count Adjustment</h3>
        <p class="modal-subtitle">Record physical inventory verification discrepancies.</p>
        <form @submit.prevent="submitAdjust">
          <div class="form-row">
            <div class="form-group">
              <label>Warehouse</label>
              <select v-model="adjustForm.warehouse_id" required class="form-select">
                <option value="" disabled>Select warehouse</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Count Date</label>
              <input v-model="adjustForm.transaction_date" type="date" required class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Justification (Required)</label>
            <input v-model="adjustForm.justification" type="text" required placeholder="Reason for count adjustment" class="form-input" />
          </div>

          <div class="lines-section">
            <h4>Counted Quantities</h4>
            <div v-for="(line, idx) in adjustForm.lines" :key="idx" class="line-row">
              <select v-model="line.item_id" required class="form-select">
                <option value="" disabled>Select Item</option>
                <option v-for="item in items" :key="item.id" :value="item.id">
                  {{ item.name }}
                </option>
              </select>
              <input v-model.number="line.actual_quantity_counted" type="number" step="0.01" min="0" required placeholder="Actual Counted" class="form-input" />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showAdjustModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Post Adjustment</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Write Off Disposal -->
    <div v-if="showWriteOffModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Authorized Stock Write-Off Disposal</h3>
        <p class="modal-subtitle">Dispose damaged, lost, or expired stock.</p>
        <form @submit.prevent="submitWriteOff">
          <div class="form-row">
            <div class="form-group">
              <label>Warehouse</label>
              <select v-model="writeOffForm.warehouse_id" required class="form-select">
                <option value="" disabled>Select warehouse</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Approval Reference</label>
              <input v-model="writeOffForm.approval_reference" type="text" required placeholder="e.g. AUTH-DISP-001" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Justification</label>
            <input v-model="writeOffForm.justification" type="text" required placeholder="Reason for disposal" class="form-input" />
          </div>

          <div class="lines-section">
            <h4>Items to Dispose</h4>
            <div v-for="(line, idx) in writeOffForm.lines" :key="idx" class="line-row">
              <select v-model="line.item_id" required class="form-select">
                <option value="" disabled>Select Item</option>
                <option v-for="item in items" :key="item.id" :value="item.id">
                  {{ item.name }}
                </option>
              </select>
              <input v-model.number="line.quantity" type="number" step="0.01" min="0.01" required placeholder="Qty" class="form-input" />
              <select v-model="line.reason" class="form-select">
                <option value="damaged">Damaged</option>
                <option value="expired">Expired</option>
                <option value="lost">Lost</option>
                <option value="theft">Theft</option>
              </select>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showWriteOffModal = false">Cancel</button>
            <button type="submit" class="btn btn-danger" :disabled="isLoading">Authorize Disposal</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Transaction Detail -->
    <div v-if="showTransactionDetailModal && selectedTransaction" class="modal-backdrop">
      <div class="modal-card modal-lg">
        <div class="modal-header">
          <h3>Transaction {{ selectedTransaction.transaction_number }}</h3>
          <span class="badge badge-success">{{ selectedTransaction.status }}</span>
        </div>
        <div class="modal-grid">
          <div><strong>Type:</strong> {{ selectedTransaction.transaction_type }}</div>
          <div><strong>Date:</strong> {{ selectedTransaction.transaction_date }}</div>
          <div v-if="selectedTransaction.source_warehouse_name">
            <strong>Source:</strong> {{ selectedTransaction.source_warehouse_name }}
          </div>
          <div v-if="selectedTransaction.destination_warehouse_name">
            <strong>Destination:</strong> {{ selectedTransaction.destination_warehouse_name }}
          </div>
          <div v-if="selectedTransaction.donor_name">
            <strong>Party:</strong> {{ selectedTransaction.donor_name }}
          </div>
          <div v-if="selectedTransaction.reference_document">
            <strong>Reference:</strong> {{ selectedTransaction.reference_document }}
          </div>
        </div>

        <h4>Ledger Entries</h4>
        <table class="data-table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Warehouse</th>
              <th>Batch</th>
              <th class="text-right">Quantity</th>
              <th class="text-right">Unit Cost</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in selectedTransaction.entries" :key="entry.id">
              <td>{{ entry.item_name }} ({{ entry.item_code }})</td>
              <td>{{ entry.warehouse_code }}</td>
              <td>{{ entry.batch_number || '—' }}</td>
              <td class="text-right font-mono" :class="Number(entry.quantity) >= 0 ? 'text-positive' : 'text-negative'">
                {{ Number(entry.quantity) >= 0 ? '+' : '' }}{{ entry.quantity }} {{ entry.unit_of_measure }}
              </td>
              <td class="text-right font-mono">${{ entry.unit_cost }}</td>
            </tr>
          </tbody>
        </table>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showTransactionDetailModal = false">Close</button>
        </div>
      </div>
    </div>

    <!-- Modal: Create Item -->
    <div v-if="showCreateItemModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Create Stock Item</h3>
        <form @submit.prevent="submitItem">
          <div class="form-group">
            <label>Category</label>
            <select v-model="newItem.category_id" required class="form-select">
              <option value="" disabled>Select category</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Item Code</label>
              <input v-model="newItem.item_code" type="text" required placeholder="e.g. MED-001" class="form-input" />
            </div>
            <div class="form-group">
              <label>Name</label>
              <input v-model="newItem.name" type="text" required placeholder="Item title" class="form-input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Unit of Measure</label>
              <input v-model="newItem.unit_of_measure" type="text" required placeholder="boxes, units, kg" class="form-input" />
            </div>
            <div class="form-group">
              <label>Item Type</label>
              <select v-model="newItem.item_type" class="form-select">
                <option value="consumable">Consumable</option>
                <option value="durable_asset">Durable Asset</option>
                <option value="relief_good">Relief Good</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <label class="checkbox-label">
              <input v-model="newItem.track_batches" type="checkbox" />
              <span>Track Batches / Lots</span>
            </label>
            <label class="checkbox-label">
              <input v-model="newItem.track_expiry" type="checkbox" />
              <span>Track Expiry Dates</span>
            </label>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Reorder Threshold</label>
              <input v-model="newItem.reorder_threshold" type="number" step="0.01" class="form-input" />
            </div>
            <div class="form-group">
              <label>Default Unit Cost</label>
              <input v-model="newItem.default_unit_cost" type="number" step="0.01" class="form-input" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showCreateItemModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Save Item</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Create Category -->
    <div v-if="showCreateCategoryModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Create Item Category</h3>
        <form @submit.prevent="submitCategory">
          <div class="form-row">
            <div class="form-group">
              <label>Name</label>
              <input v-model="newCategory.name" type="text" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Code</label>
              <input v-model="newCategory.code" type="text" required class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Parent Category (Optional)</label>
            <select v-model="newCategory.parent_id" class="form-select">
              <option :value="null">None (Top-Level)</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showCreateCategoryModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Save Category</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Create Warehouse -->
    <div v-if="showCreateWarehouseModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Create Warehouse Facility</h3>
        <form @submit.prevent="submitWarehouse">
          <div class="form-row">
            <div class="form-group">
              <label>Name</label>
              <input v-model="newWarehouse.name" type="text" required placeholder="Facility name" class="form-input" />
            </div>
            <div class="form-group">
              <label>Code</label>
              <input v-model="newWarehouse.code" type="text" required placeholder="WH-01" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Warehouse Type</label>
            <select v-model="newWarehouse.warehouse_type" class="form-select">
              <option value="central">Central Warehouse</option>
              <option value="regional_depot">Regional Depot</option>
              <option value="field_dispensary">Field Dispensary</option>
              <option value="transit">Transit Hub</option>
            </select>
          </div>
          <div class="form-group">
            <label>Address</label>
            <input v-model="newWarehouse.address" type="text" placeholder="Physical location" class="form-input" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showCreateWarehouseModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Create Warehouse</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: In-Kind Donation -->
    <div v-if="showDonationModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Record In-Kind Donation Receipt</h3>
        <p class="modal-subtitle">Record incoming donated supplies into warehouse.</p>
        <form @submit.prevent="submitDonation">
          <div class="form-row">
            <div class="form-group">
              <label>Warehouse</label>
              <select v-model="donationForm.warehouse_id" required class="form-select">
                <option value="" disabled>Select warehouse</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Donor Name</label>
              <input v-model="donationForm.donor_name" type="text" required placeholder="e.g. WHO, USAID, Foundation" class="form-input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Receipt Date</label>
              <input v-model="donationForm.transaction_date" type="date" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Reference Document</label>
              <input v-model="donationForm.reference_document" type="text" placeholder="Donation agreement #" class="form-input" />
            </div>
          </div>

          <div class="lines-section">
            <h4>Donated Items</h4>
            <div v-for="(line, idx) in donationForm.lines" :key="idx" class="line-row">
              <select v-model="line.item_id" required class="form-select">
                <option value="" disabled>Select Item</option>
                <option v-for="item in items" :key="item.id" :value="item.id">
                  {{ item.name }} ({{ item.item_code }})
                </option>
              </select>
              <input v-model.number="line.quantity" type="number" step="0.01" min="0.01" required placeholder="Qty" class="form-input" />
              <input v-model.number="line.unit_cost" type="number" step="0.01" min="0" placeholder="Est. Unit Cost" class="form-input" />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showDonationModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Post Donation Receipt</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Add Batch -->
    <div v-if="showAddBatchModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Register Item Batch / Lot</h3>
        <form @submit.prevent="submitBatch">
          <div class="form-group">
            <label>Batch / Lot Number</label>
            <input v-model="newBatch.batch_number" type="text" required placeholder="e.g. LOT-2026-X" class="form-input" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Manufacture Date</label>
              <input v-model="newBatch.manufacture_date" type="date" class="form-input" />
            </div>
            <div class="form-group">
              <label>Expiry Date</label>
              <input v-model="newBatch.expiry_date" type="date" class="form-input" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showAddBatchModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Register Batch</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Add Storage Location -->
    <div v-if="showAddLocationModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>Add Internal Storage Location</h3>
        <form @submit.prevent="submitLocation">
          <div class="form-row">
            <div class="form-group">
              <label>Name</label>
              <input v-model="newLocation.name" type="text" required placeholder="e.g. Shelf A, Row 3" class="form-input" />
            </div>
            <div class="form-group">
              <label>Code</label>
              <input v-model="newLocation.code" type="text" required placeholder="e.g. SH-A3" class="form-input" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showAddLocationModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">Add Location</button>
          </div>
        </form>
      </div>
    </div>

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

/* Attention Panel */
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
  border-left: 4px solid var(--color-warning, #f59e0b);
}

.stat-card.danger {
  border-left: 4px solid var(--color-danger, #ef4444);
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

/* Tabs */
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

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-button-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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
  text-align: left;
  font-size: 0.875rem;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.02));
  color: var(--color-text-muted);
  font-weight: 600;
}

.text-right {
  text-align: right;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.font-bold {
  font-weight: 600;
}

.text-positive {
  color: #10b981;
}

.text-negative {
  color: #ef4444;
}

.empty-state {
  text-align: center;
  padding: 2.5rem !important;
  color: var(--color-text-muted);
}

/* Badges & Tags */
.badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-success {
  background: #ecfdf5;
  color: #065f46;
}

.badge-warning {
  background: #fffbeb;
  color: #92400e;
}

.badge-muted {
  background: #f3f4f6;
  color: #4b5563;
}

.tag {
  display: inline-block;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  background: var(--color-surface-hover, #f3f4f6);
  font-size: 0.75rem;
}

.tag-blue {
  background: #eff6ff;
  color: #1d4ed8;
}

.tag-amber {
  background: #fffbeb;
  color: #b45309;
}

/* Warehouse Grid */
.warehouse-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.warehouse-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.wh-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.wh-code {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.wh-body {
  font-size: 0.875rem;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.wh-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  border-top: 1px solid var(--color-border);
  padding-top: 0.75rem;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  width: 100%;
  max-width: 540px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-lg {
  max-width: 720px;
}

.modal-subtitle {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row > * {
  flex: 1;
}

.form-input,
.form-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
}

.lines-section {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1rem;
}

.line-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.line-row > * {
  flex: 1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

/* Alerts */
.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.alert-success {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
}

.close-btn {
  margin-left: auto;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.txn-link {
  color: var(--color-primary);
  text-decoration: underline;
  cursor: pointer;
}
</style>
