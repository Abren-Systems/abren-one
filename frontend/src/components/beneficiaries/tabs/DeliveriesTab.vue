<script setup lang="ts">
import { computed, ref } from "vue";
import type { ServiceDelivery } from "@/types/beneficiary";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  deliveries: ServiceDelivery[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openRecordDelivery"): void;
}>();

const searchQuery = ref("");
const selectedType = ref<string>("all");

const filteredDeliveries = computed(() => {
  return props.deliveries.filter((d) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      d.beneficiary_name.toLowerCase().includes(q) ||
      d.service_type.toLowerCase().includes(q);
    const matchesType =
      selectedType.value === "all" || d.service_type === selectedType.value;
    return matchesSearch && matchesType;
  });
});
</script>

<template>
  <div class="deliveries-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search by recipient or service..."
          class="search-input"
        />
        <select v-model="selectedType" class="filter-select">
          <option value="all">All Service Types</option>
          <option value="food_assistance">Food Assistance</option>
          <option value="medical_support">Medical Support</option>
          <option value="cash_transfer">Cash Transfer</option>
          <option value="education_training">Education & Training</option>
          <option value="shelter_wash">Shelter / WASH</option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openRecordDelivery')"
      >
        + Record Aid Delivery
      </button>
    </div>

    <div v-if="filteredDeliveries.length === 0" class="empty-container">
      <EmptyState
        title="No Delivery Events"
        :message="
          deliveries.length === 0
            ? 'No aid distributions or service deliveries recorded yet. Record assistance provided to registered beneficiaries.'
            : 'No deliveries match your search criteria.'
        "
        action-label="+ Record Aid Delivery"
        @action="emit('openRecordDelivery')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Beneficiary Recipient</th>
            <th>Service Type</th>
            <th class="text-right">Quantity</th>
            <th>Delivery Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in filteredDeliveries" :key="d.id">
            <td><strong>{{ d.beneficiary_name }}</strong></td>
            <td>
              <span class="service-pill">{{ d.service_type.replace('_', ' ') }}</span>
            </td>
            <td class="text-right font-mono font-bold">
              {{ d.quantity }} {{ d.unit }}
            </td>
            <td>{{ d.delivery_date }}</td>
            <td>
              <StatusBadge :status="d.status" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.deliveries-tab {
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

.service-pill {
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
