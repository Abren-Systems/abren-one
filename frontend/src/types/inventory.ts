export interface ItemCategory {
  id: string;
  name: string;
  code: string;
  description: string;
  parent_id: string | null;
  parent_name: string | null;
}

export interface ItemBatch {
  id: string;
  batch_number: string;
  manufacture_date: string | null;
  expiry_date: string | null;
}

export interface ItemSummary {
  id: string;
  item_code: string;
  name: string;
  category_id: string;
  category_name: string;
  unit_of_measure: string;
  item_type: "consumable" | "durable_asset" | "relief_good";
  track_batches: boolean;
  track_expiry: boolean;
  reorder_threshold: string;
  default_unit_cost: string;
  is_active: boolean;
}

export interface ItemDetail extends ItemSummary {
  description: string;
  category_code: string;
  batches: ItemBatch[];
}

export interface StorageLocation {
  id: string;
  name: string;
  code: string;
  is_active: boolean;
}

export interface WarehouseSummary {
  id: string;
  name: string;
  code: string;
  warehouse_type: string;
  branch_id: string | null;
  custodian_id: string | null;
  is_active: boolean;
  location_count: number;
}

export interface WarehouseDetail {
  id: string;
  name: string;
  code: string;
  warehouse_type: string;
  branch_id: string | null;
  custodian_id: string | null;
  address: string;
  is_active: boolean;
  locations: StorageLocation[];
}

export interface StockBalance {
  id: string;
  item_id: string;
  item_code: string;
  item_name: string;
  unit_of_measure: string;
  warehouse_id: string;
  warehouse_name: string;
  warehouse_code: string;
  location_id: string | null;
  location_name: string | null;
  location_code: string | null;
  batch_id: string | null;
  batch_number: string | null;
  expiry_date: string | null;
  quantity_on_hand: string;
  quantity_reserved: string;
  available_quantity: string;
  reorder_threshold: string;
  is_low_stock: boolean;
}

export interface StockLedgerEntry {
  id: string;
  transaction_id: string;
  transaction_number: string;
  transaction_type: string;
  transaction_date: string;
  item_id: string;
  item_code: string;
  item_name: string;
  unit_of_measure: string;
  warehouse_id: string;
  warehouse_name: string;
  warehouse_code: string;
  location_id: string | null;
  location_name: string | null;
  batch_id: string | null;
  batch_number: string | null;
  quantity: string;
  unit_cost: string;
  program_id: string | null;
  activity_id: string | null;
}

export interface TransactionEntryLine {
  id: string;
  item_id: string;
  item_code: string;
  item_name: string;
  unit_of_measure: string;
  warehouse_id: string;
  warehouse_name: string;
  warehouse_code: string;
  location_id: string | null;
  location_name: string | null;
  batch_id: string | null;
  batch_number: string | null;
  quantity: string;
  unit_cost: string;
  program_id: string | null;
  activity_id: string | null;
}

export interface TransactionDetail {
  id: string;
  transaction_number: string;
  transaction_type: string;
  status: string;
  transaction_date: string;
  source_warehouse_id: string | null;
  source_warehouse_name: string | null;
  destination_warehouse_id: string | null;
  destination_warehouse_name: string | null;
  executed_by: string | null;
  reference_document: string;
  donor_name: string;
  notes: string;
  entries: TransactionEntryLine[];
}

export interface ReorderAlert {
  item_id: string;
  item_code: string;
  item_name: string;
  unit_of_measure: string;
  warehouse_id: string;
  warehouse_name: string;
  warehouse_code: string;
  quantity_on_hand: string;
  available_quantity: string;
  reorder_threshold: string;
  shortage_quantity: string;
}

export interface ExpiringBatchAlert {
  batch_id: string;
  batch_number: string;
  item_id: string;
  item_code: string;
  item_name: string;
  warehouse_id: string;
  warehouse_name: string;
  warehouse_code: string;
  expiry_date: string;
  days_until_expiry: number;
  quantity_on_hand: string;
  is_already_expired: boolean;
}

export interface BalanceDiscrepancy {
  warehouse_id: string;
  warehouse_name: string;
  item_id: string;
  item_name: string;
  location_id: string | null;
  batch_id: string | null;
  materialized_quantity: string;
  ledger_sum_quantity: string;
  difference: string;
}

export interface ReconciliationReport {
  total_balances_checked: number;
  discrepancies_count: number;
  is_healthy: boolean;
  discrepancies: BalanceDiscrepancy[];
}
