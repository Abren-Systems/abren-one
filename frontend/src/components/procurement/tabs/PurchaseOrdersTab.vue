<script setup lang="ts">
import type { PurchaseOrder } from "@/types/procurement";

defineProps<{
  purchaseOrders: PurchaseOrder[];
  selectedOrder: PurchaseOrder | null;
}>();

const emit = defineEmits<{
  (e: "create-order"): void;
  (e: "view-order", id: string): void;
  (e: "issue-order", id: string): void;
  (e: "receive-delivery", order: PurchaseOrder): void;
  (e: "close-order", id: string): void;
  (e: "close-detail"): void;
}>();
</script>

<template>
  <div class="tab-content">
    <div class="toolbar">
      <div></div>
      <button class="btn btn-primary btn-sm" @click="emit('create-order')">
        + Issue Purchase Order
      </button>
    </div>

    <!-- PO List Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Order #</th>
            <th>Supplier</th>
            <th>Status</th>
            <th>Total Commitment</th>
            <th>Payment Terms</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="purchaseOrders.length === 0">
            <td colspan="6" class="empty-state">No purchase orders recorded.</td>
          </tr>
          <tr v-for="o in purchaseOrders" :key="o.id">
            <td class="font-mono"><strong>{{ o.order_number }}</strong></td>
            <td>{{ o.vendor_name }}</td>
            <td>
              <span class="badge" :class="'badge-' + o.status">
                {{ o.status.toUpperCase() }}
              </span>
            </td>
            <td>{{ o.currency }} {{ Number(o.total_amount).toFixed(2) }}</td>
            <td>{{ o.payment_terms || "Standard" }}</td>
            <td>
              <div class="actions-cell">
                <button
                  class="btn btn-xs btn-outline"
                  @click="emit('view-order', o.id)"
                >
                  Details
                </button>
                <button
                  v-if="o.status === 'draft'"
                  class="btn btn-xs btn-success"
                  @click="emit('issue-order', o.id)"
                >
                  Issue
                </button>
                <button
                  v-if="o.status === 'issued'"
                  class="btn btn-xs btn-primary"
                  @click="emit('receive-delivery', o)"
                >
                  Receive Delivery
                </button>
                <button
                  v-if="o.status === 'issued'"
                  class="btn btn-xs btn-secondary"
                  @click="emit('close-order', o.id)"
                >
                  Close
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Order Detail Card -->
    <div v-if="selectedOrder" class="detail-card">
      <div class="detail-header">
        <div>
          <h3>
            PO {{ selectedOrder.order_number }} — {{ selectedOrder.vendor_name }}
          </h3>
          <span class="badge" :class="'badge-' + selectedOrder.status">
            {{ selectedOrder.status.toUpperCase() }}
          </span>
        </div>
        <button class="btn-icon" @click="emit('close-detail')">✕</button>
      </div>
      <div class="detail-body">
        <table class="data-table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Ordered</th>
              <th>Unit Price</th>
              <th>Line Total</th>
              <th>Received</th>
              <th>Accepted</th>
              <th>Outstanding</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="it in selectedOrder.items || []" :key="it.id">
              <td>{{ it.description }}</td>
              <td>{{ it.quantity }} {{ it.unit }}</td>
              <td>
                {{ selectedOrder.currency }}
                {{ Number(it.unit_price).toFixed(2) }}
              </td>
              <td>
                {{ selectedOrder.currency }}
                {{ Number(it.line_total).toFixed(2) }}
              </td>
              <td>{{ it.quantity_received || 0 }}</td>
              <td>{{ it.quantity_accepted || 0 }}</td>
              <td>
                <strong>{{ it.quantity_outstanding || 0 }}</strong>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
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

.actions-cell {
  display: flex;
  gap: 0.35rem;
}

.badge {
  display: inline-flex;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-draft {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-issued {
  background-color: #dcfce7;
  color: #166534;
}

.badge-closed {
  background-color: #f1f5f9;
  color: #475569;
}

.badge-cancelled {
  background-color: #fee2e2;
  color: #991b1b;
}

.btn-xs {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  cursor: pointer;
}

.btn-success {
  background-color: #166534;
  color: white;
  border: none;
  cursor: pointer;
}

.detail-card {
  margin-top: 1.5rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow-sm);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: var(--color-text-muted);
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem !important;
}
</style>
