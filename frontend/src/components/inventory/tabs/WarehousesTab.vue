<script setup lang="ts">
import type { WarehouseSummary } from "@/types/inventory";

defineProps<{
  warehouses: WarehouseSummary[];
}>();

const emit = defineEmits<{
  (e: "create-warehouse"): void;
  (e: "add-location", warehouseId: string): void;
  (e: "view-warehouse", warehouseId: string): void;
}>();
</script>

<template>
  <div class="tab-content">
    <div class="toolbar">
      <div></div>
      <button class="btn btn-primary btn-sm" @click="emit('create-warehouse')">
        + New Warehouse
      </button>
    </div>

    <div v-if="warehouses.length === 0" class="empty-state">
      No storage warehouses registered yet.
    </div>

    <div v-else class="warehouse-grid">
      <div v-for="wh in warehouses" :key="wh.id" class="warehouse-card">
        <div class="wh-header">
          <div>
            <h3>{{ wh.name }}</h3>
            <span class="wh-code font-mono">{{ wh.code }}</span>
          </div>
          <span
            class="badge"
            :class="wh.is_active ? 'badge-success' : 'badge-muted'"
          >
            {{ wh.is_active ? "Active" : "Inactive" }}
          </span>
        </div>
        <div class="wh-body">
          <p>
            <strong>Type:</strong> {{ wh.warehouse_type.replace(/_/g, " ") }}
          </p>
          <p><strong>Internal Locations:</strong> {{ wh.location_count }}</p>
        </div>
        <div class="wh-footer">
          <button
            class="btn btn-secondary btn-sm"
            @click="emit('add-location', wh.id)"
          >
            + Location
          </button>
          <button
            class="btn btn-ghost btn-sm"
            @click="emit('view-warehouse', wh.id)"
          >
            View Details
          </button>
        </div>
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

.warehouse-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.warehouse-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.wh-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.wh-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.wh-code {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.font-mono {
  font-family: monospace;
}

.wh-body {
  margin: 0.5rem 0 1rem 0;
  font-size: 0.875rem;
  color: var(--color-text);
}

.wh-body p {
  margin: 0.25rem 0;
}

.wh-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  border-top: 1px solid var(--color-border);
  padding-top: 0.75rem;
}

.badge-success {
  background-color: #dcfce7;
  color: #166534;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-muted {
  background-color: #f1f5f9;
  color: #64748b;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
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
  padding: 3rem 1rem;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
}
</style>
