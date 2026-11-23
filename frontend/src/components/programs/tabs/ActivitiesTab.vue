<script setup lang="ts">
import { computed, ref } from "vue";
import type { Activity, Project } from "@/types/program";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  activities: Activity[];
  projects: Project[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateActivity"): void;
}>();

const searchQuery = ref("");
const selectedProject = ref<string>("all");

const projectMap = computed(() => {
  const map: Record<string, string> = {};
  for (const prj of props.projects) {
    map[prj.id] = prj.name;
  }
  return map;
});

const filteredActivities = computed(() => {
  return props.activities.filter((act) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch = act.name.toLowerCase().includes(q);
    const matchesProject =
      selectedProject.value === "all" || act.project_id === selectedProject.value;
    return matchesSearch && matchesProject;
  });
});
</script>

<template>
  <div class="activities-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search activities..."
          class="search-input"
        />
        <select v-model="selectedProject" class="filter-select">
          <option value="all">All Projects</option>
          <option v-for="prj in projects" :key="prj.id" :value="prj.id">
            {{ prj.name }}
          </option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateActivity')"
      >
        + Add Activity
      </button>
    </div>

    <div v-if="filteredActivities.length === 0" class="empty-container">
      <EmptyState
        title="No Activities Found"
        :message="
          activities.length === 0
            ? 'No operational activities recorded yet. Activities represent concrete tasks and deliverables under projects.'
            : 'No activities match your search criteria.'
        "
        action-label="+ Add Activity"
        @action="emit('openCreateActivity')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Activity Name</th>
            <th>Parent Project</th>
            <th>Due Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="act in filteredActivities" :key="act.id">
            <td><strong>{{ act.name }}</strong></td>
            <td>{{ projectMap[act.project_id] || "—" }}</td>
            <td>{{ act.due_date || "—" }}</td>
            <td>
              <StatusBadge :status="act.status" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.activities-tab {
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
