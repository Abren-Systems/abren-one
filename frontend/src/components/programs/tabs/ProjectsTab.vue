<script setup lang="ts">
import { computed, ref } from "vue";
import type { Program, Project } from "@/types/program";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";

const props = defineProps<{
  projects: Project[];
  programs: Program[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "openCreateProject"): void;
}>();

const searchQuery = ref("");
const selectedProgram = ref<string>("all");

const programMap = computed(() => {
  const map: Record<string, string> = {};
  for (const p of props.programs) {
    map[p.id] = p.name;
  }
  return map;
});

const filteredProjects = computed(() => {
  return props.projects.filter((prj) => {
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      prj.name.toLowerCase().includes(q) ||
      (prj.description && prj.description.toLowerCase().includes(q));
    const matchesProgram =
      selectedProgram.value === "all" || prj.program_id === selectedProgram.value;
    return matchesSearch && matchesProgram;
  });
});
</script>

<template>
  <div class="projects-tab">
    <div class="toolbar">
      <div class="search-filters">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search projects..."
          class="search-input"
        />
        <select v-model="selectedProgram" class="filter-select">
          <option value="all">All Programs</option>
          <option v-for="p in programs" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="emit('openCreateProject')"
      >
        + Create Project
      </button>
    </div>

    <div v-if="filteredProjects.length === 0" class="empty-container">
      <EmptyState
        title="No Projects Found"
        :message="
          projects.length === 0
            ? 'No deliverable projects created yet. Projects link operational field work to high-level strategic programs.'
            : 'No projects match your search criteria.'
        "
        action-label="+ Create Project"
        @action="emit('openCreateProject')"
      />
    </div>

    <div v-else class="card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Project Name</th>
            <th>Parent Program</th>
            <th>Budget Currency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="prj in filteredProjects" :key="prj.id">
            <td><strong>{{ prj.name }}</strong></td>
            <td>{{ programMap[prj.program_id] || "—" }}</td>
            <td><code>{{ prj.budget_currency }}</code></td>
            <td>
              <StatusBadge :status="prj.status" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.projects-tab {
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
