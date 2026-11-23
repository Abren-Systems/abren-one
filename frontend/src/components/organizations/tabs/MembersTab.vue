<script setup lang="ts">
import { computed, ref } from "vue";
import type { Member } from "@/types/organization";
import EmptyState from "@/components/common/EmptyState.vue";

const props = defineProps<{
  members: Member[];
  isLoading?: boolean;
}>();

const searchQuery = ref("");

const filteredMembers = computed(() => {
  const q = searchQuery.value.toLowerCase();
  return props.members.filter(
    (m) =>
      m.username.toLowerCase().includes(q) ||
      (m.email && m.email.toLowerCase().includes(q)) ||
      m.role.toLowerCase().includes(q)
  );
});
</script>

<template>
  <div class="members-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search members by username, email or role..."
          class="search-input"
        />
      </div>
    </div>

    <div v-if="filteredMembers.length === 0" class="empty-container">
      <EmptyState
        title="No Members Found"
        :message="
          members.length === 0
            ? 'No team members yet. Members are added via invitation from the account settings.'
            : 'No members match your search criteria.'
        "
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in filteredMembers" :key="m.membership_id">
            <td><strong>{{ m.username }}</strong></td>
            <td>{{ m.email || "–" }}</td>
            <td><span class="role-pill">{{ m.role }}</span></td>
            <td><span class="badge badge-active">{{ m.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.members-tab {
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

.role-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background-color: #f1f5f9;
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-primary);
  text-transform: capitalize;
}

.badge-active {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background-color: #dcfce7;
  color: #166534;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}
</style>
