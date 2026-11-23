import { api } from "../client";
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

export const inventoryApi = {
  // Categories
  async getCategories(): Promise<ItemCategory[]> {
    return api.get<ItemCategory[]>("/api/v1/inventory/categories/");
  },

  async createCategory(data: {
    name: string;
    code: string;
    description?: string;
    parent_id?: string | null;
  }): Promise<{ category_id: string }> {
    return api.post("/api/v1/inventory/categories/", data);
  },

  // Items
  async getItems(): Promise<ItemSummary[]> {
    return api.get<ItemSummary[]>("/api/v1/inventory/items/");
  },

  async getItemDetail(id: string): Promise<ItemDetail> {
    return api.get<ItemDetail>(`/api/v1/inventory/items/${id}/`);
  },

  async createItem(data: {
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
  }): Promise<{ item_id: string }> {
    return api.post("/api/v1/inventory/items/", data);
  },

  async createBatch(
    itemId: string,
    data: {
      batch_number: string;
      manufacture_date?: string;
      expiry_date?: string;
    }
  ): Promise<{ batch_id: string }> {
    return api.post(`/api/v1/inventory/items/${itemId}/batches/`, data);
  },

  // Warehouses
  async getWarehouses(): Promise<WarehouseSummary[]> {
    return api.get<WarehouseSummary[]>("/api/v1/inventory/warehouses/");
  },

  async getWarehouseDetail(id: string): Promise<WarehouseDetail> {
    return api.get<WarehouseDetail>(`/api/v1/inventory/warehouses/${id}/`);
  },

  async createWarehouse(data: {
    name: string;
    code: string;
    warehouse_type: string;
    address?: string;
  }): Promise<{ warehouse_id: string }> {
    return api.post("/api/v1/inventory/warehouses/", data);
  },

  async createLocation(
    warehouseId: string,
    data: {
      name: string;
      code: string;
    }
  ): Promise<{ location_id: string }> {
    return api.post(`/api/v1/inventory/warehouses/${warehouseId}/locations/`, data);
  },

  // Balances & Alerts
  async getBalances(): Promise<StockBalance[]> {
    return api.get<StockBalance[]>("/api/v1/inventory/balances/");
  },

  async getReconciliation(): Promise<ReconciliationReport> {
    return api.get<ReconciliationReport>("/api/v1/inventory/balances/reconciliation/");
  },

  async getAlerts(): Promise<{
    reorder_alerts: ReorderAlert[];
    expiring_batches: ExpiringBatchAlert[];
  }> {
    return api.get("/api/v1/inventory/alerts/");
  },

  // Ledger & Transactions
  async getLedgerEntries(): Promise<StockLedgerEntry[]> {
    return api.get<StockLedgerEntry[]>("/api/v1/inventory/ledger/");
  },

  async getTransactionDetail(id: string): Promise<TransactionDetail> {
    return api.get<TransactionDetail>(`/api/v1/inventory/transactions/${id}/`);
  },

  // Stock Movements
  async postMovement(type: string, payload: unknown): Promise<{ transaction_id: string }> {
    return api.post(`/api/v1/inventory/transactions/${type}/`, payload);
  },

  // Intake Bridge
  async getPendingGrns(): Promise<PendingGRN[]> {
    return api.get<PendingGRN[]>("/api/v1/inventory/pending-grns/");
  },

  async postGrnIntake(payload: unknown): Promise<{ transaction_id: string }> {
    return api.post("/api/v1/inventory/transactions/receive-purchase/", payload);
  },
};
