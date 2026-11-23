<script setup lang="ts">
import type { GoodsReceiptNote } from "@/types/procurement";

defineProps<{
  goodsReceipts: GoodsReceiptNote[];
}>();

const emit = defineEmits<{
  (e: "inspect-grn", grn: GoodsReceiptNote): void;
}>();
</script>

<template>
  <div class="tab-content">
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
            <td colspan="6" class="empty-state">No goods receipt notes recorded.</td>
          </tr>
          <tr v-for="g in goodsReceipts" :key="g.id">
            <td class="font-mono"><strong>{{ g.receipt_number }}</strong></td>
            <td>{{ g.order_number }}</td>
            <td>{{ g.receipt_type.toUpperCase() }}</td>
            <td>{{ g.received_date }}</td>
            <td>
              <span v-if="g.is_fully_inspected" class="badge badge-success">
                {{ g.has_rejections ? "INSPECTED (REJECTIONS)" : "INSPECTED (ACCEPTED)" }}
              </span>
              <span v-else class="badge badge-warning">PENDING INSPECTION</span>
            </td>
            <td>
              <button
                v-if="!g.is_fully_inspected"
                class="btn btn-xs btn-primary"
                @click="emit('inspect-grn', g)"
              >
                Inspect & Reconcile
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
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

.badge {
  display: inline-flex;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-success {
  background-color: #dcfce7;
  color: #166534;
}

.badge-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.btn-xs {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem !important;
}
</style>
