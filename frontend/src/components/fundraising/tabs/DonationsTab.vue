<script setup lang="ts">
import { computed, ref } from "vue";
import type { Donation } from "@/types/fundraising";
import EmptyState from "@/components/common/EmptyState.vue";

const props = defineProps<{
  donations: Donation[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openRecordDonation"): void;
}>();

const searchQuery = ref("");
const selectedMethod = ref<string>("all");

const filteredDonations = computed(() => {
  return props.donations.filter((d) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      d.donor_name.toLowerCase().includes(q) ||
      (d.reference && d.reference.toLowerCase().includes(q));
    const matchesMethod =
      selectedMethod.value === "all" || d.payment_method === selectedMethod.value;
    return matchesSearch && matchesMethod;
  });
});
</script>

<template>
  <div class="donations-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search donations by donor or reference..."
          class="search-input"
        />
        <select v-model="selectedMethod" class="filter-select">
          <option value="all">All Methods</option>
          <option value="bank_transfer">Bank Transfer</option>
          <option value="cash">Cash</option>
          <option value="check">Check</option>
          <option value="online">Online</option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openRecordDonation')"
      >
        + Record Incoming Contribution
      </button>
    </div>

    <div v-if="filteredDonations.length === 0" class="empty-container">
      <EmptyState
        title="No Contributions Recorded"
        :message="
          donations.length === 0
            ? 'No donations recorded yet. Record incoming contributions from individual and institutional supporters.'
            : 'No contributions match your search criteria.'
        "
        action-label="+ Record Incoming Contribution"
        @action="emit('openRecordDonation')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Donor Supporter</th>
            <th class="text-right">Amount</th>
            <th>Payment Method</th>
            <th>Reference</th>
            <th>Received Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in filteredDonations" :key="d.id">
            <td><strong>{{ d.donor_name }}</strong></td>
            <td class="text-right font-mono font-bold">
              {{ d.amount }} {{ d.currency }}
            </td>
            <td>
              <span class="method-pill">{{ d.payment_method.replace('_', ' ') }}</span>
            </td>
            <td><code>{{ d.reference || "—" }}</code></td>
            <td>{{ new Date(d.received_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.donations-tab {
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

.method-pill {
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
