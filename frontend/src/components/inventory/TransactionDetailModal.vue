<script setup lang="ts">
import type { TransactionDetail } from "@/types/inventory";

defineProps<{
  show: boolean;
  transaction: TransactionDetail | null;
}>();

const emit = defineEmits<{
  (e: "close"): void;
}>();
</script>

<template>
  <div v-if="show && transaction" class="modal-backdrop">
    <div class="modal-card modal-lg">
      <div class="modal-header">
        <h3>Transaction {{ transaction.transaction_number }}</h3>
        <span class="badge badge-success">{{ transaction.status }}</span>
      </div>
      <div class="modal-grid">
        <div><strong>Type:</strong> {{ transaction.transaction_type }}</div>
        <div><strong>Date:</strong> {{ transaction.transaction_date }}</div>
        <div v-if="transaction.source_warehouse_name">
          <strong>Source:</strong> {{ transaction.source_warehouse_name }}
        </div>
        <div v-if="transaction.destination_warehouse_name">
          <strong>Destination:</strong> {{ transaction.destination_warehouse_name }}
        </div>
        <div v-if="transaction.donor_name">
          <strong>Party:</strong> {{ transaction.donor_name }}
        </div>
        <div v-if="transaction.reference_document">
          <strong>Reference:</strong> {{ transaction.reference_document }}
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
          <tr v-for="entry in transaction.entries" :key="entry.id">
            <td>{{ entry.item_name }} ({{ entry.item_code }})</td>
            <td>{{ entry.warehouse_code }}</td>
            <td>{{ entry.batch_number || "—" }}</td>
            <td
              class="text-right font-mono"
              :class="Number(entry.quantity) >= 0 ? 'text-positive' : 'text-negative'"
            >
              {{ Number(entry.quantity) >= 0 ? "+" : "" }}{{ entry.quantity }} {{ entry.unit_of_measure }}
            </td>
            <td class="text-right font-mono">${{ entry.unit_cost }}</td>
          </tr>
        </tbody>
      </table>

      <div class="modal-actions">
        <button type="button" class="btn btn-secondary" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  max-width: 520px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-lg {
  max-width: 760px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
}

.modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  font-size: 0.875rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th,
.data-table td {
  padding: 0.625rem 0.875rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.data-table th {
  background: var(--color-background);
  font-weight: 600;
  color: var(--color-text-muted);
}

.text-right {
  text-align: right;
}

.font-mono {
  font-family: monospace;
}

.text-positive {
  color: #16a34a;
  font-weight: 600;
}

.text-negative {
  color: #dc2626;
  font-weight: 600;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge-success {
  background: rgba(22, 163, 74, 0.15);
  color: #16a34a;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn-secondary {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text);
}
</style>
