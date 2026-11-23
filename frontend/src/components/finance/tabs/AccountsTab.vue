<script setup lang="ts">
import { computed, ref } from "vue";
import type { Account } from "@/types/finance";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  accounts: Account[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateAccount"): void;
}>();

const searchQuery = ref("");
const selectedType = ref<string>("all");

const filteredAccounts = computed(() => {
  return props.accounts.filter((acc) => {
    const matchesSearch =
      acc.code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      acc.name.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesType =
      selectedType.value === "all" || acc.account_type === selectedType.value;
    return matchesSearch && matchesType;
  });
});
</script>

<template>
  <div class="accounts-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search by code or name..."
          class="search-input"
        />
        <select v-model="selectedType" class="filter-select">
          <option value="all">All Types</option>
          <option value="asset">Asset (Debit)</option>
          <option value="liability">Liability (Credit)</option>
          <option value="equity">Equity (Credit)</option>
          <option value="revenue">Revenue (Credit)</option>
          <option value="expense">Expense (Debit)</option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateAccount')"
      >
        + Add Account
      </button>
    </div>

    <div v-if="filteredAccounts.length === 0" class="empty-container">
      <EmptyState
        title="No Accounts Found"
        :message="
          accounts.length === 0
            ? 'The Chart of Accounts is empty. Add your first general ledger account to start recording financial transactions.'
            : 'No accounts match your current search and filter criteria.'
        "
        action-label="+ Add Account"
        @action="emit('openCreateAccount')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Account Name</th>
            <th>Classification</th>
            <th>Currency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="acc in filteredAccounts" :key="acc.id">
            <td class="code-cell">{{ acc.code }}</td>
            <td><strong>{{ acc.name }}</strong></td>
            <td>
              <span class="type-pill" :class="`type-${acc.account_type}`">
                {{ acc.account_type.toUpperCase() }}
              </span>
            </td>
            <td>{{ acc.currency }}</td>
            <td>
              <StatusBadge :status="acc.is_active ? 'active' : 'inactive'" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.accounts-tab {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.search-filters {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  max-width: 480px;
}

.search-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: #ffffff;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: #ffffff;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.btn-primary {
  background-color: #1e3a8a;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #172554;
}

.card {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.table-card {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th {
  background-color: #f8fafc;
  color: #475569;
  text-align: left;
  padding: 0.75rem 1rem;
  font-weight: 600;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
}

.data-table tr:hover {
  background-color: #f8fafc;
}

.code-cell {
  font-family: monospace;
  font-weight: 600;
  color: #1e3a8a;
}

.type-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.type-asset {
  background-color: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.type-liability {
  background-color: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
}

.type-equity {
  background-color: #faf5ff;
  color: #7e22ce;
  border: 1px solid #e9d5ff;
}

.type-revenue {
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.type-expense {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.empty-container {
  padding: 2rem 0;
}
</style>
