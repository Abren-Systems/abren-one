<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { api } from "@/api/client";
import { useTenantStore } from "@/stores/tenant";
import type { Activity, Program, Project } from "@/types/program";

const tenantStore = useTenantStore();

const programs = ref<Program[]>([]);
const projects = ref<Project[]>([]);
const activities = ref<Activity[]>([]);
const isLoading = ref(false);

// Forms
const newProgName = ref("");
const newProgDesc = ref("");

const newProjName = ref("");
const newProjProgId = ref("");

const newActName = ref("");
const newActProjId = ref("");

async function loadData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  try {
    const [p, prj, act] = await Promise.all([
      api.get<Program[]>("/api/v1/programs/").catch(() => []),
      api.get<Project[]>("/api/v1/programs/projects/").catch(() => []),
      api.get<Activity[]>("/api/v1/programs/activities/").catch(() => []),
    ]);
    programs.value = p;
    projects.value = prj;
    activities.value = act;

    if (programs.value.length > 0 && !newProjProgId.value) {
      newProjProgId.value = programs.value[0].id;
    }
    if (projects.value.length > 0 && !newActProjId.value) {
      newActProjId.value = projects.value[0].id;
    }
  } finally {
    isLoading.value = false;
  }
}

async function createProgram() {
  if (!newProgName.value) return;
  try {
    await api.post("/api/v1/programs/", {
      name: newProgName.value,
      description: newProgDesc.value,
    });
    newProgName.value = "";
    newProgDesc.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to create program");
  }
}

async function createProject() {
  if (!newProjName.value || !newProjProgId.value) return;
  try {
    await api.post("/api/v1/programs/projects/", {
      program_id: newProjProgId.value,
      name: newProjName.value,
    });
    newProjName.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to create project");
  }
}

async function createActivity() {
  if (!newActName.value || !newActProjId.value) return;
  try {
    await api.post("/api/v1/programs/activities/", {
      project_id: newActProjId.value,
      name: newActName.value,
    });
    newActName.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to create activity");
  }
}

watch(() => tenantStore.currentOrganizationId, () => loadData());
onMounted(() => loadData());
</script>

<template>
  <div class="programs-page">
    <div class="page-header">
      <h1 class="page-title">Program Delivery Hierarchy</h1>
      <p class="page-subtitle">Strategic long-term programs, deliverable projects, and operational tasks.</p>
    </div>

    <!-- Programs Card -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Strategic Programs</h3>
        <span class="badge badge-active">{{ programs.length }} Active</span>
      </div>

      <form @submit.prevent="createProgram" class="inline-form">
        <input v-model="newProgName" type="text" placeholder="Program Name (e.g. Health & Nutrition)" class="form-input" required />
        <input v-model="newProgDesc" type="text" placeholder="Description" class="form-input" />
        <button type="submit" class="btn btn-primary">Create Program</button>
      </form>

      <table class="data-table" v-if="programs.length > 0">
        <thead>
          <tr>
            <th>Program Name</th>
            <th>Description</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in programs" :key="p.id">
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.description || "–" }}</td>
            <td><span class="badge badge-active">{{ p.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No programs created yet.</p>
    </section>

    <!-- Projects Card -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Projects</h3>
        <span class="badge badge-active">{{ projects.length }} Total</span>
      </div>

      <form @submit.prevent="createProject" class="inline-form" v-if="programs.length > 0">
        <select v-model="newProjProgId" class="form-select select-inline" required>
          <option v-for="p in programs" :key="p.id" :value="p.id">
            Under: {{ p.name }}
          </option>
        </select>
        <input v-model="newProjName" type="text" placeholder="Project Name (e.g. Water Distribution)" class="form-input" required />
        <button type="submit" class="btn btn-primary">Create Project</button>
      </form>

      <table class="data-table" v-if="projects.length > 0">
        <thead>
          <tr>
            <th>Project Name</th>
            <th>Currency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="prj in projects" :key="prj.id">
            <td><strong>{{ prj.name }}</strong></td>
            <td><code>{{ prj.budget_currency }}</code></td>
            <td><span class="badge badge-active">{{ prj.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No projects created yet.</p>
    </section>

    <!-- Activities Card -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Operational Activities</h3>
        <span class="badge badge-active">{{ activities.length }} Total</span>
      </div>

      <form @submit.prevent="createActivity" class="inline-form" v-if="projects.length > 0">
        <select v-model="newActProjId" class="form-select select-inline" required>
          <option v-for="prj in projects" :key="prj.id" :value="prj.id">
            Under: {{ prj.name }}
          </option>
        </select>
        <input v-model="newActName" type="text" placeholder="Activity Name (e.g. Daily Ration Distribution)" class="form-input" required />
        <button type="submit" class="btn btn-primary">Create Activity</button>
      </form>

      <table class="data-table" v-if="activities.length > 0">
        <thead>
          <tr>
            <th>Activity Name</th>
            <th>Due Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="act in activities" :key="act.id">
            <td><strong>{{ act.name }}</strong></td>
            <td>{{ act.due_date || "–" }}</td>
            <td><span class="badge badge-active">{{ act.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No activities created yet.</p>
    </section>
  </div>
</template>

<style scoped>
.programs-page {
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
.select-inline {
  max-width: 220px;
}
.empty-state {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  padding: 1rem 0;
}
</style>
