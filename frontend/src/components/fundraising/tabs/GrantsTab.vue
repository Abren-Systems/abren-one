<script setup lang="ts">
import { computed, ref } from "vue";
import type { Grant } from "@/types/fundraising";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  grants: Grant[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateGrant"): void;
  (e: "awardGrant", grantId: string): void;
  (e: "activateGrant", grantId: string): void;
  (e: "closeGrant", grantId: string): void;
}>();

const searchQuery = ref("");
const selectedStatus = ref<string>("all");

const filteredGrants = computed(() => {
  return props.grants.filter((g) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      g.title.toLowerCase().includes(q) ||
      g.reference_code.toLowerCase().includes(q) ||
      g.donor_name.toLowerCase().includes(q);
    const matchesStatus =
      selectedStatus.value === "all" || g.status === selectedStatus.value;
    return matchesSearch && matchesStatus;
  });
});
</script>

<template>
  <div class="grants-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search by title, donor, or reference code..."
          class="search-input"
        />
        <select v-model="selectedStatus" class="filter-select">
          <option value="all">All Statuses</option>
          <option value="proposed">Proposed</option>
          <option value="awarded">Awarded</option>
          <option value="active">Active</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateGrant')"
      >
        + Register Institutional Grant
      </button>
    </div>

    <div v-if="filteredGrants.length === 0" class="empty-container">
      <EmptyState
        title="No Grants Found"
        :message="
          grants.length === 0
            ? 'No institutional grants recorded yet. Register grant agreements to track funding windows and budgets.'
            : 'No grants match your search criteria.'
        "
        action-label="+ Register Institutional Grant"
        @action="emit('openCreateGrant')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Grant Title</th>
            <th>Donor Supporter</th>
            <th>Reference Code</th>
            <th class="text-right">Total Amount</th>
            <th>Status</th>
            <th class="text-right">Lifecycle Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in filteredGrants" :key="g.id">
            <td><strong>{{ g.title }}</strong></td>
            <td>{{ g.donor_name }}</td>
            <td><code>{{ g.reference_code }}</code></td>
            <td class="text-right font-mono font-bold">
              {{ g.total_amount }} {{ g.currency }}
            </td>
            <td>
              <StatusBadge :status="g.status" />
            </td>
            <td class="text-right actions-cell">
              <button
                v-if="g.status === 'proposed'"
                type="button"
                class="btn btn-xs btn-award"
                :disabled="isLoading"
                @click="emit('awardGrant', g.id)"
              >
                Award
              </button>
              <button
                v-else-if="g.status === 'awarded'"
                type="button"
                class="btn btn-xs btn-activate"
                :disabled="isLoading"
                @click="emit('activateGrant', g.id)"
              >
                Activate
              </button>
              <button
                v-else-if="g.status === 'active'"
                type="button"
                class="btn btn-xs btn-close-grant"
                :disabled="isLoading"
                @click="emit('closeGrant', g.id)"
              >
                Close
              </button>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.grants-tab {
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
  max-width: 520px;
}

.search-input {
  flex: 2;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background-color: var(--color-surface);
  color: var(--color-text);
}

.filter-select {
  flex: 1;
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

.text-right {
  text-align: right;
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: 600;
}

.actions-cell {
  white-space: nowrap;
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

.btn-xs {
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
}

.btn-award {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.btn-award:hover {
  background-color: #fde68a;
}

.btn-activate {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.btn-activate:hover {
  background-color: #bbf7d0;
}

.btn-close-grant {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.btn-close-grant:hover {
  background-color: #fecaca;
}

.text-muted {
  color: var(--color-text-muted);
}
</style>
