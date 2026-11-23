<script setup lang="ts">
import type { Vendor } from "@/types/procurement";

defineProps<{
  vendors: Vendor[];
}>();

const emit = defineEmits<{
  (e: "create-vendor"): void;
}>();
</script>

<template>
  <div class="tab-content">
    <div class="toolbar">
      <div></div>
      <button class="btn btn-primary btn-sm" @click="emit('create-vendor')">
        + Register Supplier
      </button>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Tax ID</th>
            <th>Contact</th>
            <th>Email</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="vendors.length === 0">
            <td colspan="6" class="empty-state">No suppliers registered.</td>
          </tr>
          <tr v-for="v in vendors" :key="v.id">
            <td><strong>{{ v.name }}</strong></td>
            <td>{{ v.vendor_type }}</td>
            <td class="font-mono">{{ v.tax_id || "—" }}</td>
            <td>{{ v.contact_name || "—" }}</td>
            <td>{{ v.email || "—" }}</td>
            <td>
              <span
                class="badge"
                :class="v.is_active ? 'badge-success' : 'badge-danger'"
              >
                {{ v.is_active ? "ACTIVE" : "DEACTIVATED" }}
              </span>
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

.badge-danger {
  background-color: #fee2e2;
  color: #991b1b;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem !important;
}
</style>
