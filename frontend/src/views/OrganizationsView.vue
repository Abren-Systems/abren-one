<script setup lang="ts">
import { ref } from "vue";
import { useOrganizations } from "@/composables/useOrganizations";
import BranchesTab from "@/components/organizations/tabs/BranchesTab.vue";
import DepartmentsTab from "@/components/organizations/tabs/DepartmentsTab.vue";
import MembersTab from "@/components/organizations/tabs/MembersTab.vue";
import CreateBranchModal from "@/components/organizations/modals/CreateBranchModal.vue";
import CreateDepartmentModal from "@/components/organizations/modals/CreateDepartmentModal.vue";
import type { CreateBranchPayload, CreateDepartmentPayload } from "@/api/modules/organizations";

const {
  branches,
  departments,
  members,
  isLoading,
  errorMessage,
  successMessage,
  createBranch,
  createDepartment,
  clearMessages,
} = useOrganizations();

// Tab state
const activeTab = ref<"branches" | "departments" | "members">("branches");

// Modal state
const showCreateBranch = ref(false);
const showCreateDepartment = ref(false);

async function handleCreateBranch(payload: CreateBranchPayload) {
  await createBranch(payload);
  showCreateBranch.value = false;
}

async function handleCreateDepartment(payload: CreateDepartmentPayload) {
  await createDepartment(payload);
  showCreateDepartment.value = false;
}
</script>

<template>
  <div class="orgs-page">
    <div class="page-header">
      <h1 class="page-title">Organizational Structure & Members</h1>
      <p class="page-subtitle">
        Manage operational branches, functional departments, and team membership roles.
      </p>
    </div>

    <!-- Alert messages -->
    <div v-if="errorMessage" class="alert alert-error" role="alert">
      {{ errorMessage }}
      <button class="alert-close" @click="clearMessages">×</button>
    </div>
    <div v-if="successMessage" class="alert alert-success" role="status">
      {{ successMessage }}
      <button class="alert-close" @click="clearMessages">×</button>
    </div>

    <!-- Tab navigation -->
    <div class="tab-nav" role="tablist">
      <button
        role="tab"
        :aria-selected="activeTab === 'branches'"
        :class="['tab-btn', { active: activeTab === 'branches' }]"
        @click="activeTab = 'branches'"
      >
        Branches
        <span class="tab-badge">{{ branches.length }}</span>
      </button>
      <button
        role="tab"
        :aria-selected="activeTab === 'departments'"
        :class="['tab-btn', { active: activeTab === 'departments' }]"
        @click="activeTab = 'departments'"
      >
        Departments
        <span class="tab-badge">{{ departments.length }}</span>
      </button>
      <button
        role="tab"
        :aria-selected="activeTab === 'members'"
        :class="['tab-btn', { active: activeTab === 'members' }]"
        @click="activeTab = 'members'"
      >
        Members
        <span class="tab-badge">{{ members.length }}</span>
      </button>
    </div>

    <!-- Tab panels -->
    <div class="tab-content">
      <BranchesTab
        v-if="activeTab === 'branches'"
        :branches="branches"
        :is-loading="isLoading"
        @open-create-branch="showCreateBranch = true"
      />
      <DepartmentsTab
        v-else-if="activeTab === 'departments'"
        :departments="departments"
        :is-loading="isLoading"
        @open-create-department="showCreateDepartment = true"
      />
      <MembersTab
        v-else-if="activeTab === 'members'"
        :members="members"
        :is-loading="isLoading"
      />
    </div>

    <!-- Modals -->
    <CreateBranchModal
      :open="showCreateBranch"
      :is-loading="isLoading"
      @close="showCreateBranch = false"
      @create="handleCreateBranch"
    />
    <CreateDepartmentModal
      :open="showCreateDepartment"
      :is-loading="isLoading"
      @close="showCreateDepartment = false"
      @create="handleCreateDepartment"
    />
  </div>
</template>

<style scoped>
.orgs-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.page-subtitle {
  font-size: 0.9375rem;
  color: var(--color-text-muted);
  margin: 0;
}

.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
}

.alert-error {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.alert-success {
  background-color: #f0fdf4;
  color: #166534;
  border: 1px solid #86efac;
}

.alert-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.125rem;
  color: inherit;
  opacity: 0.6;
  padding: 0 0.25rem;
}

.alert-close:hover {
  opacity: 1;
}

.tab-nav {
  display: flex;
  gap: 0.25rem;
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 0;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-text-muted);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s ease;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
}

.tab-btn:hover {
  color: var(--color-text);
  background-color: var(--color-surface-hover);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.35rem;
  background-color: var(--color-border);
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-muted);
}

.tab-btn.active .tab-badge {
  background-color: var(--color-primary);
  color: #ffffff;
}

.tab-content {
  min-height: 300px;
}
</style>
