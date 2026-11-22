<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { api } from "@/api/client";
import { useTenantStore } from "@/stores/tenant";
import type { Branch, Department, Member } from "@/types/organization";

const tenantStore = useTenantStore();

const branches = ref<Branch[]>([]);
const departments = ref<Department[]>([]);
const members = ref<Member[]>([]);
const isLoading = ref(false);

// Form models
const newBranchName = ref("");
const newBranchCode = ref("");
const newDeptName = ref("");
const newDeptCode = ref("");

async function loadData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  try {
    const [b, d, m] = await Promise.all([
      api.get<Branch[]>("/api/v1/organizations/branches/").catch(() => []),
      api.get<Department[]>("/api/v1/organizations/departments/").catch(() => []),
      api.get<Member[]>("/api/v1/organizations/members/").catch(() => []),
    ]);
    branches.value = b;
    departments.value = d;
    members.value = m;
  } finally {
    isLoading.value = false;
  }
}

async function createBranch() {
  if (!newBranchName.value || !newBranchCode.value) return;
  try {
    await api.post("/api/v1/organizations/branches/", {
      name: newBranchName.value,
      code: newBranchCode.value,
    });
    newBranchName.value = "";
    newBranchCode.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to create branch");
  }
}

async function createDepartment() {
  if (!newDeptName.value || !newDeptCode.value) return;
  try {
    await api.post("/api/v1/organizations/departments/", {
      name: newDeptName.value,
      code: newDeptCode.value,
    });
    newDeptName.value = "";
    newDeptCode.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to create department");
  }
}

watch(() => tenantStore.currentOrganizationId, () => loadData());
onMounted(() => loadData());
</script>

<template>
  <div class="orgs-page">
    <div class="page-header">
      <h1 class="page-title">Organizational Structure & Members</h1>
      <p class="page-subtitle">Manage branches, operational departments, and membership roles.</p>
    </div>

    <!-- Branches Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Operational Branches</h3>
        <span class="badge badge-active">{{ branches.length }} Total</span>
      </div>

      <form @submit.prevent="createBranch" class="inline-form">
        <input v-model="newBranchName" type="text" placeholder="Branch Name (e.g. Regional Office)" class="form-input" required />
        <input v-model="newBranchCode" type="text" placeholder="Code (e.g. RO-01)" class="form-input code-input" required />
        <button type="submit" class="btn btn-primary">Add Branch</button>
      </form>

      <table class="data-table" v-if="branches.length > 0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Code</th>
            <th>Headquarters</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in branches" :key="b.id">
            <td><strong>{{ b.name }}</strong></td>
            <td><code>{{ b.code }}</code></td>
            <td>{{ b.is_headquarters ? "Yes" : "No" }}</td>
            <td><span class="badge badge-active">Active</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No branches registered yet.</p>
    </section>

    <!-- Departments Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Functional Departments</h3>
        <span class="badge badge-active">{{ departments.length }} Total</span>
      </div>

      <form @submit.prevent="createDepartment" class="inline-form">
        <input v-model="newDeptName" type="text" placeholder="Department Name (e.g. Logistics)" class="form-input" required />
        <input v-model="newDeptCode" type="text" placeholder="Code (e.g. LOG)" class="form-input code-input" required />
        <button type="submit" class="btn btn-primary">Add Department</button>
      </form>

      <table class="data-table" v-if="departments.length > 0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Code</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in departments" :key="d.id">
            <td><strong>{{ d.name }}</strong></td>
            <td><code>{{ d.code }}</code></td>
            <td><span class="badge badge-active">Active</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No departments registered yet.</p>
    </section>

    <!-- Members Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Team Memberships</h3>
        <span class="badge badge-active">{{ members.length }} Members</span>
      </div>

      <table class="data-table" v-if="members.length > 0">
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in members" :key="m.membership_id">
            <td><strong>{{ m.username }}</strong></td>
            <td>{{ m.email || "–" }}</td>
            <td><span class="role-pill">{{ m.role }}</span></td>
            <td><span class="badge badge-active">{{ m.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No members loaded.</p>
    </section>
  </div>
</template>

<style scoped>
.orgs-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.section-card {
  display: flex;
  flex-direction: column;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.inline-form {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.code-input {
  max-width: 140px;
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
.empty-state {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  padding: 1rem 0;
}
</style>
