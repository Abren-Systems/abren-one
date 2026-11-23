import { ref, watch, onMounted, getCurrentInstance } from "vue";
import { inventoryApi } from "@/api/modules/inventory";
import { useTenantStore } from "@/stores/tenant";
import type {
  ExpiringBatchAlert,
  ItemCategory,
  ItemDetail,
  ItemSummary,
  PendingGRN,
  ReconciliationReport,
  ReorderAlert,
  StockBalance,
  StockLedgerEntry,
  TransactionDetail,
  WarehouseDetail,
  WarehouseSummary,
} from "@/types/inventory";

export function useInventory() {
  const tenantStore = useTenantStore();

  const categories = ref<ItemCategory[]>([]);
  const items = ref<ItemSummary[]>([]);
  const warehouses = ref<WarehouseSummary[]>([]);
  const balances = ref<StockBalance[]>([]);
  const ledgerEntries = ref<StockLedgerEntry[]>([]);
  const reorderAlerts = ref<ReorderAlert[]>([]);
  const expiringBatches = ref<ExpiringBatchAlert[]>([]);
  const pendingGrns = ref<PendingGRN[]>([]);

  const selectedItem = ref<ItemDetail | null>(null);
  const selectedWarehouse = ref<WarehouseDetail | null>(null);
  const selectedTransaction = ref<TransactionDetail | null>(null);
  const reconciliationReport = ref<ReconciliationReport | null>(null);

  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadData() {
    if (!tenantStore.currentOrganizationId) return;
    isLoading.value = true;
    errorMessage.value = null;

    try {
      const [catRes, itemRes, whRes, balRes, ledgerRes, alertsRes] =
        await Promise.all([
          inventoryApi.getCategories(),
          inventoryApi.getItems(),
          inventoryApi.getWarehouses(),
          inventoryApi.getBalances(),
          inventoryApi.getLedgerEntries(),
          inventoryApi.getAlerts(),
        ]);

      categories.value = catRes;
      items.value = itemRes;
      warehouses.value = whRes;
      balances.value = balRes;
      ledgerEntries.value = ledgerRes;
      reorderAlerts.value = alertsRes.reorder_alerts;
      expiringBatches.value = alertsRes.expiring_batches;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load inventory data.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadPendingGrns() {
    try {
      pendingGrns.value = await inventoryApi.getPendingGrns();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load pending GRNs.";
    }
  }

  async function fetchItemDetail(id: string) {
    try {
      selectedItem.value = await inventoryApi.getItemDetail(id);
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to fetch item detail.";
    }
  }

  async function fetchWarehouseDetail(id: string) {
    try {
      selectedWarehouse.value = await inventoryApi.getWarehouseDetail(id);
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to fetch warehouse detail.";
    }
  }

  async function fetchTransactionDetail(id: string) {
    try {
      selectedTransaction.value = await inventoryApi.getTransactionDetail(id);
      return selectedTransaction.value;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to fetch transaction detail.";
      return null;
    }
  }

  async function createCategory(data: {
    name: string;
    code: string;
    description?: string;
    parent_id?: string | null;
  }) {
    isLoading.value = true;
    try {
      const res = await inventoryApi.createCategory(data);
      successMessage.value = "Category created successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to create category.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createItem(data: {
    category_id: string;
    item_code: string;
    name: string;
    description?: string;
    unit_of_measure: string;
    item_type: string;
    track_batches: boolean;
    track_expiry: boolean;
    reorder_threshold: string;
    default_unit_cost: string;
  }) {
    isLoading.value = true;
    try {
      const res = await inventoryApi.createItem(data);
      successMessage.value = "Item created successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to create item.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createBatch(
    itemId: string,
    data: {
      batch_number: string;
      manufacture_date?: string;
      expiry_date?: string;
    }
  ) {
    isLoading.value = true;
    try {
      const res = await inventoryApi.createBatch(itemId, data);
      successMessage.value = "Batch registered successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to register batch.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createWarehouse(data: {
    name: string;
    code: string;
    warehouse_type: string;
    address?: string;
  }) {
    isLoading.value = true;
    try {
      const res = await inventoryApi.createWarehouse(data);
      successMessage.value = "Warehouse created successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to create warehouse.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createLocation(
    warehouseId: string,
    data: { name: string; code: string }
  ) {
    isLoading.value = true;
    try {
      const res = await inventoryApi.createLocation(warehouseId, data);
      successMessage.value = "Location added successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to add location.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function recordMovement(type: string, payload: unknown) {
    isLoading.value = true;
    try {
      const res = await inventoryApi.postMovement(type, payload);
      successMessage.value = "Stock movement recorded successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to record stock movement.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function intakeGrn(payload: unknown) {
    isLoading.value = true;
    try {
      const res = await inventoryApi.postGrnIntake(payload);
      successMessage.value = "Goods receipt stock intake recorded successfully.";
      await loadData();
      await loadPendingGrns();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to record goods receipt intake.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function runReconciliation() {
    isLoading.value = true;
    try {
      const res = await inventoryApi.getReconciliation();
      reconciliationReport.value = res;
      if (res.is_healthy) {
        successMessage.value = `Audit complete: All ${res.total_balances_checked} balances match ledger.`;
      } else {
        errorMessage.value = `Warning: ${res.discrepancies_count} discrepancies detected.`;
      }
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Reconciliation failed.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearMessages() {
    errorMessage.value = null;
    successMessage.value = null;
  }

  watch(() => tenantStore.currentOrganizationId, () => {
    loadData();
  });

  if (getCurrentInstance()) {
    onMounted(() => {
      loadData();
    });
  }

  return {
    // State
    categories,
    items,
    warehouses,
    balances,
    ledgerEntries,
    reorderAlerts,
    expiringBatches,
    pendingGrns,
    selectedItem,
    selectedWarehouse,
    selectedTransaction,
    reconciliationReport,
    isLoading,
    errorMessage,
    successMessage,

    // Actions
    loadData,
    loadPendingGrns,
    fetchItemDetail,
    fetchWarehouseDetail,
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
  };
}
