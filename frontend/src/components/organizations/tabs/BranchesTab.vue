<script setup lang="ts">
import { computed, ref } from "vue";
import type { Branch } from "@/types/organization";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  branches: Branch[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateBranch"): void;
}>();

const searchQuery = ref("");

const filteredBranches = computed(() => {
  const q = searchQuery.value.toLowerCase();
  return props.branches.filter(
    (b) =>
      b.name.toLowerCase().includes(q) || b.code.toLowerCase().includes(q)
  );
});
</script>

<template>
  <div class="branches-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search branches by name or code..."
          class="search-input"
        />
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateBranch')"
      >
        + Add Branch
      </button>
    </div>

    <div v-if="filteredBranches.length === 0" class="empty-container">
      <EmptyState
        title="No Branches Found"
        :message="
          branches.length === 0
            ? 'No operational branches registered yet. Add branches to represent geographic or operational offices.'
            : 'No branches match your search criteria.'
        "
        action-label="+ Add Branch"
        @action="emit('openCreateBranch')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Branch Name</th>
            <th>Code</th>
            <th>Headquarters</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in filteredBranches" :key="b.id">
            <td><strong>{{ b.name }}</strong></td>
            <td><code>{{ b.code }}</code></td>
            <td>{{ b.is_headquarters ? "Yes" : "No" }}</td>
            <td>
              <StatusBadge :status="b.is_active ? 'active' : 'inactive'" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.branches-tab {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-filters {
  display: flex;
  gap: 0.75rem;
  flex: 1;
  max-width: 420px;
}

.search-input {
  width: 100%;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background-color: var(--color-surface);
  color: var(--color-text);
}

.empty-container {
  padding: 2rem 0;
}

.table-card {
  padding: 0;
  overflow: hidden;
  border-radius: var(--radius-md);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th,
.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.875rem;
}

.data-table th {
  background-color: #f8fafc;
  color: var(--color-text-muted);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.btn {
  padding: 0.55rem 1.15rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.btn-primary {
  background-color: var(--color-primary);
  color: #ffffff;
}

.btn-primary:hover {
  filter: brightness(0.92);
}
</style>
