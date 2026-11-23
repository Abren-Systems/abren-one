<script setup lang="ts">
import { ref, computed } from "vue";
import type { StockLedgerEntry, WarehouseSummary } from "@/types/inventory";

const props = defineProps<{
  ledgerEntries: StockLedgerEntry[];
  warehouses: WarehouseSummary[];
}>();

const emit = defineEmits<{
  (e: "view-transaction", id: string): void;
  (e: "open-receive-purchase"): void;
  (e: "open-donation"): void;
  (e: "open-transfer"): void;
  (e: "open-issue"): void;
  (e: "open-adjust"): void;
  (e: "open-write-off"): void;
}>();

const warehouseFilter = ref("");

const filteredLedger = computed(() => {
  return props.ledgerEntries.filter((e) => {
    return !warehouseFilter.value || e.warehouse_id === warehouseFilter.value;
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
      </div>
      <div class="action-button-group">
        <button class="btn btn-primary btn-sm" @click="emit('open-receive-purchase')">
          <span>📦</span> Receive Purchase (GRN)
        </button>
        <button class="btn btn-secondary btn-sm" @click="emit('open-donation')">
          <span>🎁</span> In-Kind Donation
        </button>
        <button class="btn btn-secondary btn-sm" @click="emit('open-transfer')">
          <span>🔄</span> Transfer Stock
        </button>
        <button class="btn btn-secondary btn-sm" @click="emit('open-issue')">
          <span>📤</span> Issue Supplies
        </button>
        <button class="btn btn-secondary btn-sm" @click="emit('open-adjust')">
          <span>⚖️</span> Count Adjust
        </button>
        <button class="btn btn-secondary btn-sm" @click="emit('open-write-off')">
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
              <a
                href="#"
                class="txn-link"
                @click.prevent="emit('view-transaction', e.transaction_id)"
              >
                {{ e.transaction_number }}
              </a>
            </td>
            <td>
              <span class="badge" :class="'badge-' + e.transaction_type">
                {{ e.transaction_type.replace(/_/g, " ") }}
              </span>
            </td>
            <td>{{ e.warehouse_code }}</td>
            <td>{{ e.item_name }}</td>
            <td>{{ e.batch_number || "—" }}</td>
            <td
              class="text-right font-mono"
              :class="Number(e.quantity) >= 0 ? 'text-positive' : 'text-negative'"
            >
              {{ Number(e.quantity) >= 0 ? "+" : "" }}{{ e.quantity }} {{ e.unit_of_measure }}
            </td>
            <td class="text-right font-mono">${{ e.unit_cost }}</td>
            <td>
              <button
                class="btn btn-ghost btn-xs"
                @click="emit('view-transaction', e.transaction_id)"
              >
                View
              </button>
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
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.action-button-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.font-mono {
  font-family: monospace;
}

.text-right {
  text-align: right;
}

.text-positive {
  color: #166534;
  font-weight: 600;
}

.text-negative {
  color: #991b1b;
  font-weight: 600;
}

.txn-link {
  color: var(--color-primary);
  text-decoration: underline;
  cursor: pointer;
}

.badge {
  display: inline-flex;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.btn-xs {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  cursor: pointer;
}

.btn-ghost:hover {
  background: #f1f5f9;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem !important;
}
</style>
