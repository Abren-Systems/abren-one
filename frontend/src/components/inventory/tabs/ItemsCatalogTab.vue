<script setup lang="ts">
import { ref, computed } from "vue";
import type { ItemCategory, ItemSummary } from "@/types/inventory";

const props = defineProps<{
  items: ItemSummary[];
  categories: ItemCategory[];
}>();

const emit = defineEmits<{
  (e: "create-category"): void;
  (e: "create-item"): void;
  (e: "add-batch", itemId: string): void;
  (e: "view-item", itemId: string): void;
}>();

const search = ref("");
const categoryFilter = ref("");

const filteredItems = computed(() => {
  return props.items.filter((i) => {
    const matchesSearch =
      !search.value ||
      i.name.toLowerCase().includes(search.value.toLowerCase()) ||
      i.item_code.toLowerCase().includes(search.value.toLowerCase());
    const matchesCat =
      !categoryFilter.value || i.category_id === categoryFilter.value;
    return matchesSearch && matchesCat;
  });
});
</script>

<template>
  <div class="tab-content">
    <div class="toolbar">
      <div class="filter-group">
        <input
          v-model="search"
          type="text"
          placeholder="Search items by code or name..."
          class="form-input"
        />
        <select v-model="categoryFilter" class="form-select">
          <option value="">All Categories</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
      </div>
      <div class="action-button-group">
        <button class="btn btn-secondary btn-sm" @click="emit('create-category')">
          + Category
        </button>
        <button class="btn btn-primary btn-sm" @click="emit('create-item')">
          + New Item
        </button>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Item Code</th>
            <th>Name</th>
            <th>Category</th>
            <th>UOM</th>
            <th>Type</th>
            <th>Batch / Expiry</th>
            <th class="text-right">Reorder Threshold</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td colspan="9" class="empty-state">No cataloged items found.</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td class="font-mono font-bold">{{ item.item_code }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.category_name }}</td>
            <td>{{ item.unit_of_measure }}</td>
            <td><span class="tag">{{ item.item_type }}</span></td>
            <td>
              <span v-if="item.track_batches" class="tag tag-blue">Batches</span>
              <span v-if="item.track_expiry" class="tag tag-amber">Expiry</span>
              <span v-if="!item.track_batches && !item.track_expiry">—</span>
            </td>
            <td class="text-right font-mono">{{ item.reorder_threshold }}</td>
            <td>
              <span
                class="badge"
                :class="item.is_active ? 'badge-success' : 'badge-muted'"
              >
                {{ item.is_active ? "Active" : "Inactive" }}
              </span>
            </td>
            <td>
              <button
                v-if="item.track_batches"
                class="btn btn-ghost btn-xs"
                @click="emit('add-batch', item.id)"
              >
                + Batch
              </button>
              <button
                class="btn btn-ghost btn-xs"
                @click="emit('view-item', item.id)"
              >
                Details
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

.font-bold {
  font-weight: 700;
}

.text-right {
  text-align: right;
}

.tag {
  display: inline-block;
  padding: 0.1rem 0.4rem;
  background-color: #f1f5f9;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.tag-blue {
  background-color: #eff6ff;
  color: #1d4ed8;
}

.tag-amber {
  background-color: #fffbeb;
  color: #b45309;
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

.btn-xs {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  margin-right: 0.35rem;
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
