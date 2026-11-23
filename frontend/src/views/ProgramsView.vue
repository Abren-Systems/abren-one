<script setup lang="ts">
import { ref } from "vue";
import { usePrograms } from "@/composables/usePrograms";
import type {
  CreateActivityPayload,
  CreateProgramPayload,
  CreateProjectPayload,
} from "@/types/program";

import ProgramsTab from "@/components/programs/tabs/ProgramsTab.vue";
import ProjectsTab from "@/components/programs/tabs/ProjectsTab.vue";
import ActivitiesTab from "@/components/programs/tabs/ActivitiesTab.vue";

import CreateProgramModal from "@/components/programs/modals/CreateProgramModal.vue";
import CreateProjectModal from "@/components/programs/modals/CreateProjectModal.vue";
import CreateActivityModal from "@/components/programs/modals/CreateActivityModal.vue";

const activeTab = ref<"programs" | "projects" | "activities">("programs");

const {
  programs,
  projects,
  activities,
  isLoading,
  errorMessage,
  successMessage,
  createProgram,
  createProject,
  createActivity,
  clearMessages,
} = usePrograms();

const showCreateProgramModal = ref(false);
const showCreateProjectModal = ref(false);
const showCreateActivityModal = ref(false);

async function handleCreateProgram(payload: CreateProgramPayload) {
  try {
    await createProgram(payload);
    showCreateProgramModal.value = false;
  } catch {
    // Handled in composable
  }
}

async function handleCreateProject(payload: CreateProjectPayload) {
  try {
    await createProject(payload);
    showCreateProjectModal.value = false;
  } catch {
    // Handled in composable
  }
}

async function handleCreateActivity(payload: CreateActivityPayload) {
  try {
    await createActivity(payload);
    showCreateActivityModal.value = false;
  } catch {
    // Handled in composable
  }
}
</script>

<template>
  <div class="programs-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Program Delivery Hierarchy</h1>
        <p class="page-subtitle">
          Strategic long-term programs, deliverable projects, and operational tasks.
        </p>
      </div>
    </div>

    <!-- Feedback messages -->
    <div v-if="errorMessage" class="alert alert-error">
      <span>{{ errorMessage }}</span>
      <button type="button" class="alert-close" @click="clearMessages">✕</button>
    </div>

    <div v-if="successMessage" class="alert alert-success">
      <span>{{ successMessage }}</span>
      <button type="button" class="alert-close" @click="clearMessages">✕</button>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-nav">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'programs' }"
        @click="activeTab = 'programs'"
      >
        Strategic Programs ({{ programs.length }})
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'projects' }"
        @click="activeTab = 'projects'"
      >
        Projects ({{ projects.length }})
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'activities' }"
        @click="activeTab = 'activities'"
      >
        Operational Activities ({{ activities.length }})
      </button>
    </div>

    <!-- Tab Contents -->
    <div class="tab-content">
      <ProgramsTab
        v-if="activeTab === 'programs'"
        :programs="programs"
        :is-loading="isLoading"
        @open-create-program="showCreateProgramModal = true"
      />

      <ProjectsTab
        v-else-if="activeTab === 'projects'"
        :projects="projects"
        :programs="programs"
        :is-loading="isLoading"
        @open-create-project="showCreateProjectModal = true"
      />

      <ActivitiesTab
        v-else-if="activeTab === 'activities'"
        :activities="activities"
        :projects="projects"
        :is-loading="isLoading"
        @open-create-activity="showCreateActivityModal = true"
      />
    </div>

    <!-- Modals -->
    <CreateProgramModal
      :open="showCreateProgramModal"
      :is-loading="isLoading"
      @close="showCreateProgramModal = false"
      @create="handleCreateProgram"
    />

    <CreateProjectModal
      :open="showCreateProjectModal"
      :programs="programs"
      :is-loading="isLoading"
      @close="showCreateProjectModal = false"
      @create="handleCreateProject"
    />

    <CreateActivityModal
      :open="showCreateActivityModal"
      :projects="projects"
      :is-loading="isLoading"
      @close="showCreateActivityModal = false"
      @create="handleCreateActivity"
    />
  </div>
</template>

<style scoped>
.programs-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.tabs-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.tab-btn {
  background: transparent;
  border: none;
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--color-text);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  display: flex;
  flex-direction: column;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-success {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.alert-close {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: inherit;
  opacity: 0.7;
}

.alert-close:hover {
  opacity: 1;
}
</style>
