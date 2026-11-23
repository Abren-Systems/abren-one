<script setup lang="ts">
import { computed, ref } from "vue";
import type { Beneficiary } from "@/types/beneficiary";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  beneficiaries: Beneficiary[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openRegister"): void;
}>();

const searchQuery = ref("");
const selectedVuln = ref<string>("all");

const filteredBeneficiaries = computed(() => {
  return props.beneficiaries.filter((b) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      b.display_name.toLowerCase().includes(q) ||
      (b.identification_number && b.identification_number.toLowerCase().includes(q));
    const matchesVuln =
      selectedVuln.value === "all" || b.vulnerability_level === selectedVuln.value;
    return matchesSearch && matchesVuln;
  });
});
</script>

<template>
  <div class="beneficiaries-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search by name, household, or ID..."
          class="search-input"
        />
        <select v-model="selectedVuln" class="filter-select">
          <option value="all">All Vulnerability Levels</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openRegister')"
      >
        + Register Beneficiary
      </button>
    </div>

    <div v-if="filteredBeneficiaries.length === 0" class="empty-container">
      <EmptyState
        title="No Beneficiaries Found"
        :message="
          beneficiaries.length === 0
            ? 'No recipient profiles registered yet. Register an individual, household, or community to track aid deliveries.'
            : 'No beneficiaries match your search criteria.'
        "
        action-label="+ Register Beneficiary"
        @action="emit('openRegister')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name / Household</th>
            <th>Type</th>
            <th>ID / Ration #</th>
            <th>Vulnerability</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in filteredBeneficiaries" :key="b.id">
            <td><strong>{{ b.display_name }}</strong></td>
            <td>
              <span class="type-pill">{{ b.beneficiary_type }}</span>
            </td>
            <td><code>{{ b.identification_number || "—" }}</code></td>
            <td>
              <span class="vuln-badge" :class="'vuln-' + b.vulnerability_level">
                {{ b.vulnerability_level }}
              </span>
            </td>
            <td>
              <StatusBadge :status="b.status" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.beneficiaries-tab {
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

.type-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background-color: #f1f5f9;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: capitalize;
}

.vuln-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.vuln-low {
  background-color: #e0f2fe;
  color: #0369a1;
}

.vuln-medium {
  background-color: #fef3c7;
  color: #92400e;
}

.vuln-high {
  background-color: #ffedd5;
  color: #c2410c;
}

.vuln-critical {
  background-color: #fee2e2;
  color: #991b1b;
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
