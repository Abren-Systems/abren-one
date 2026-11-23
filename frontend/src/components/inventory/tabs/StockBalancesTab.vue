<script setup lang="ts">
import { ref, computed } from "vue";
import type { StockBalance, WarehouseSummary } from "@/types/inventory";

const props = defineProps<{
  balances: StockBalance[];
  warehouses: WarehouseSummary[];
}>();

const warehouseFilter = ref("");
const lowStockOnly = ref(false);

const filteredBalances = computed(() => {
  return props.balances.filter((b) => {
    const matchesWh =
      !warehouseFilter.value || b.warehouse_id === warehouseFilter.value;
    const matchesLow = !lowStockOnly.value || b.is_low_stock;
    return matchesWh && matchesLow;
  });
});
</script>

<template>
  <div class="tab-content">
    <div class="toolbar">
      <div class="filter-group">
        <select v-model="warehouseFilter" class="form-select">
          <option value="">All Warehouses</option>
          <option v-for="w in warehouses" :key="w.id" :value="w.id">
            {{ w.name }} ({{ w.code }})
          </option>
        </select>
        <label class="checkbox-label">
          <input v-model="lowStockOnly" type="checkbox" />
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
            <td>{{ b.location_code || "—" }}</td>
            <td>{{ b.batch_number || "—" }}</td>
            <td>{{ b.expiry_date || "—" }}</td>
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
</template>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  cursor: pointer;
}

.table-container {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-surface);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: var(--color-text-muted);
}

.code-cell {
  font-weight: 600;
  color: var(--color-primary);
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: 700;
}

.text-right {
  text-align: right;
}

.badge-success {
  background-color: #dcfce7;
  color: #166534;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-warning {
  background-color: #fef3c7;
  color: #92400e;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem !important;
}
</style>
