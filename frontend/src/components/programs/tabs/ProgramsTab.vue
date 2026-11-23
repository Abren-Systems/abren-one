<script setup lang="ts">
import { computed, ref } from "vue";
import type { Program } from "@/types/program";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  programs: Program[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateProgram"): void;
}>();

const searchQuery = ref("");

const filteredPrograms = computed(() => {
  return props.programs.filter((p) => {
    const q = searchQuery.value.toLowerCase();
    return (
      p.name.toLowerCase().includes(q) ||
      (p.description && p.description.toLowerCase().includes(q))
    );
  });
});
</script>

<template>
  <div class="programs-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search programs by name or description..."
          class="search-input"
        />
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateProgram')"
      >
        + Create Strategic Program
      </button>
    </div>

    <div v-if="filteredPrograms.length === 0" class="empty-container">
      <EmptyState
        title="No Programs Found"
        :message="
          programs.length === 0
            ? 'No high-level humanitarian programs defined yet. Create strategic programs (e.g. Health & Nutrition, Emergency Relief) to organize projects.'
            : 'No programs match your search criteria.'
        "
        action-label="+ Create Strategic Program"
        @action="emit('openCreateProgram')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Program Name</th>
            <th>Strategic Purpose / Description</th>
            <th>Duration</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in filteredPrograms" :key="p.id">
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.description || "—" }}</td>
            <td>
              <span v-if="p.start_date || p.end_date" class="date-range">
                {{ p.start_date || "—" }} to {{ p.end_date || "—" }}
              </span>
              <span v-else class="text-muted">Ongoing</span>
            </td>
            <td>
              <StatusBadge :status="p.status || (p.is_active ? 'active' : 'inactive')" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.programs-tab {
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

.date-range {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.text-muted {
  color: var(--color-text-muted);
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
