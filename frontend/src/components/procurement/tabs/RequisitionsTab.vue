<script setup lang="ts">
import type {
  PurchaseRequisition,
  RequisitionFulfillment,
} from "@/types/procurement";

defineProps<{
  requisitions: PurchaseRequisition[];
  selectedRequisition: PurchaseRequisition | null;
  selectedFulfillment: RequisitionFulfillment | null;
}>();

const emit = defineEmits<{
  (e: "create-requisition"): void;
  (e: "view-requisition", id: string): void;
  (e: "submit-requisition", id: string): void;
  (e: "approve-requisition", id: string): void;
  (e: "close-detail"): void;
}>();
</script>

<template>
  <div class="tab-content">
    <div class="toolbar">
      <div></div>
      <button class="btn btn-primary btn-sm" @click="emit('create-requisition')">
        + Raise Requisition
      </button>
    </div>

    <!-- Requisition List Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Number</th>
            <th>Title</th>
            <th>Authorization</th>
            <th>Est. Cost</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="requisitions.length === 0">
            <td colspan="6" class="empty-state">No purchase requisitions found.</td>
          </tr>
          <tr v-for="r in requisitions" :key="r.id">
            <td class="font-mono">{{ r.requisition_number }}</td>
            <td><strong>{{ r.title }}</strong></td>
            <td>
              <span class="badge" :class="'badge-' + r.authorization_status">
                {{ r.authorization_status.toUpperCase() }}
              </span>
            </td>
            <td>{{ r.currency }} {{ Number(r.total_estimated_cost).toFixed(2) }}</td>
            <td>{{ new Date(r.created_at).toLocaleDateString() }}</td>
            <td>
              <div class="actions-cell">
                <button
                  class="btn btn-xs btn-outline"
                  @click="emit('view-requisition', r.id)"
                >
                  View
                </button>
                <button
                  v-if="r.authorization_status === 'draft'"
                  class="btn btn-xs btn-secondary"
                  @click="emit('submit-requisition', r.id)"
                >
                  Submit
                </button>
                <button
                  v-if="r.authorization_status === 'submitted'"
                  class="btn btn-xs btn-success"
                  @click="emit('approve-requisition', r.id)"
                >
                  Approve
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Requisition Detail Card -->
    <div v-if="selectedRequisition" class="detail-card">
      <div class="detail-header">
        <div>
          <h3>
            {{ selectedRequisition.requisition_number }}:
            {{ selectedRequisition.title }}
          </h3>
          <span
            class="badge"
            :class="'badge-' + selectedRequisition.authorization_status"
          >
            {{ selectedRequisition.authorization_status.toUpperCase() }}
          </span>
          <span v-if="selectedFulfillment" class="badge badge-outline ml-2">
            Fulfillment: {{ selectedFulfillment.fulfillment_position }}
          </span>
        </div>
        <button class="btn-icon" @click="emit('close-detail')">✕</button>
      </div>
      <div class="detail-body">
        <table class="data-table">
          <thead>
            <tr>
              <th>Description</th>
              <th>Requested</th>
              <th>Est. Unit Price</th>
              <th>Line Total</th>
              <th>Ordered</th>
              <th>Outstanding</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in selectedRequisition.items || []"
              :key="item.id"
            >
              <td>{{ item.description }}</td>
              <td>{{ item.quantity }} {{ item.unit }}</td>
              <td>
                {{ selectedRequisition.currency }}
                {{ Number(item.estimated_unit_price).toFixed(2) }}
              </td>
              <td>
                {{ selectedRequisition.currency }}
                {{ Number(item.line_total).toFixed(2) }}
              </td>
              <td>{{ item.allocated_quantity || 0 }} {{ item.unit }}</td>
              <td>
                <strong>
                  {{ item.outstanding_quantity ?? item.quantity }}
                  {{ item.unit }}
                </strong>
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

.badge-submitted {
  background-color: #e0e7ff;
  color: #3730a3;
}

.badge-approved {
  background-color: #dcfce7;
  color: #166534;
}

.badge-rejected {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-outline {
  background-color: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}

.ml-2 {
  margin-left: 0.5rem;
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
