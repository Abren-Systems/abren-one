<script setup lang="ts">
import { computed, ref } from "vue";
import type { JournalEntry } from "@/types/finance";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  journalEntries: JournalEntry[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateEntry"): void;
  (e: "postEntry", entryId: string): void;
  (e: "reverseEntry", entry: JournalEntry): void;
}>();

const searchQuery = ref("");
const selectedStatus = ref<string>("all");

const filteredEntries = computed(() => {
  return props.journalEntries.filter((entry) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      entry.entry_number.toLowerCase().includes(q) ||
      entry.memo.toLowerCase().includes(q);
    const matchesStatus =
      selectedStatus.value === "all" || entry.status === selectedStatus.value;
    return matchesSearch && matchesStatus;
  });
});
</script>

<template>
  <div class="journal-entries-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search by entry # or memo..."
          class="search-input"
        />
        <select v-model="selectedStatus" class="filter-select">
          <option value="all">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="posted">Posted</option>
          <option value="reversed">Reversed</option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateEntry')"
      >
        + Record Journal Entry
      </button>
    </div>

    <div v-if="filteredEntries.length === 0" class="empty-container">
      <EmptyState
        title="No Journal Entries"
        :message="
          journalEntries.length === 0
            ? 'No double-entry journal entries recorded yet. Record your first balanced entry or wait for operational transactions to post.'
            : 'No journal entries match your search and filter criteria.'
        "
        action-label="+ Record Journal Entry"
        @action="emit('openCreateEntry')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Entry #</th>
            <th>Date</th>
            <th>Memo / Description</th>
            <th class="text-right">Total Amount</th>
            <th>Status</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in filteredEntries" :key="entry.id">
            <td class="code-cell">{{ entry.entry_number }}</td>
            <td class="date-cell">{{ entry.entry_date }}</td>
            <td class="memo-cell">
              <span class="memo-text">{{ entry.memo }}</span>
              <span v-if="entry.reversal_of_id" class="reversal-tag">
                Reversal
              </span>
            </td>
            <td class="text-right font-mono font-bold">
              {{ entry.total_amount }} {{ entry.currency }}
            </td>
            <td>
              <StatusBadge :status="entry.status" />
            </td>
            <td class="text-right actions-cell">
              <button
                v-if="entry.status === 'draft'"
                type="button"
                class="btn btn-xs btn-post"
                :disabled="isLoading"
                @click="emit('postEntry', entry.id)"
              >
                Post
              </button>
              <button
                v-if="entry.status === 'posted'"
                type="button"
                class="btn btn-xs btn-reverse"
                :disabled="isLoading"
                @click="emit('reverseEntry', entry)"
              >
                Reverse
              </button>
              <span v-if="entry.status === 'reversed'" class="text-muted">
                —
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.journal-entries-tab {
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

.btn-xs {
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 4px;
}

.btn-post {
  background-color: #2563eb;
  color: #ffffff;
}

.btn-post:hover {
  background-color: #1d4ed8;
}

.btn-reverse {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.btn-reverse:hover {
  background-color: #fecaca;
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

.date-cell {
  white-space: nowrap;
  color: #64748b;
  font-size: 0.8rem;
}

.memo-cell {
  max-width: 400px;
}

.memo-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reversal-tag {
  display: inline-block;
  margin-top: 0.2rem;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  font-size: 0.65rem;
  font-weight: 700;
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.text-right {
  text-align: right;
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: 700;
}

.text-muted {
  color: #94a3b8;
  font-size: 0.8rem;
}

.empty-container {
  padding: 2rem 0;
}
</style>
