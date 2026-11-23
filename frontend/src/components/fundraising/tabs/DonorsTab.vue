<script setup lang="ts">
import { computed, ref } from "vue";
import type { Donor } from "@/types/fundraising";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  donors: Donor[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateDonor"): void;
}>();

const searchQuery = ref("");
const selectedType = ref<string>("all");

const filteredDonors = computed(() => {
  return props.donors.filter((d) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      d.name.toLowerCase().includes(q) ||
      (d.email && d.email.toLowerCase().includes(q));
    const matchesType =
      selectedType.value === "all" || d.donor_type === selectedType.value;
    return matchesSearch && matchesType;
  });
});
</script>

<template>
  <div class="donors-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search donors by name or email..."
          class="search-input"
        />
        <select v-model="selectedType" class="filter-select">
          <option value="all">All Types</option>
          <option value="foundation">Foundation</option>
          <option value="individual">Individual</option>
          <option value="corporation">Corporation</option>
          <option value="government">Government</option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateDonor')"
      >
        + Add Supporter / Donor
      </button>
    </div>

    <div v-if="filteredDonors.length === 0" class="empty-container">
      <EmptyState
        title="No Donors Found"
        :message="
          donors.length === 0
            ? 'No supporters or institutional donors registered yet. Add a donor profile to track pledges and grants.'
            : 'No donors match your search criteria.'
        "
        action-label="+ Add Supporter / Donor"
        @action="emit('openCreateDonor')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in filteredDonors" :key="d.id">
            <td><strong>{{ d.name }}</strong></td>
            <td>
              <span class="type-pill">{{ d.donor_type }}</span>
            </td>
            <td>{{ d.email || "—" }}</td>
            <td>{{ d.phone || "—" }}</td>
            <td>
              <StatusBadge :status="d.status || (d.is_active ? 'active' : 'inactive')" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.donors-tab {
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
