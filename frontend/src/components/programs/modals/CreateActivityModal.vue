<script setup lang="ts">
import { ref, watch } from "vue";
import type { CreateActivityPayload, Project } from "@/types/program";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  projects: Project[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: CreateActivityPayload): void;
}>();

const projectId = ref("");
const name = ref("");
const dueDate = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      projectId.value = props.projects[0]?.id || "";
      name.value = "";
      dueDate.value = "";
    }
  }
);

function handleSubmit() {
  if (!projectId.value || !name.value.trim()) return;

  emit("create", {
    project_id: projectId.value,
    name: name.value.trim(),
    due_date: dueDate.value || null,
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Add Operational Activity" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-group">
        <label for="act-prj">Parent Project *</label>
        <select id="act-prj" v-model="projectId" class="form-input" required>
          <option value="" disabled>Select Project</option>
          <option v-for="prj in projects" :key="prj.id" :value="prj.id">
            {{ prj.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="act-name">Activity Name *</label>
        <input
          id="act-name"
          v-model="name"
          type="text"
          placeholder="e.g. Borehole Pump Maintenance Check"
          required
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label for="act-due">Due Date (Optional)</label>
        <input
          id="act-due"
          v-model="dueDate"
          type="date"
          class="form-input"
        />
      </div>

      <div class="modal-actions">
        <button
          type="button"
          class="btn btn-secondary"
          :disabled="isLoading"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="isLoading || !projectId || !name.trim()"
        >
          {{ isLoading ? "Adding..." : "Add Activity" }}
        </button>
      </div>
    </form>
  </ModalDialog>
</template>

<style scoped>
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.form-input {
  padding: 0.55rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: #ffffff;
  color: #0f172a;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.btn {
  padding: 0.55rem 1.15rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.btn-secondary {
  background-color: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.btn-secondary:hover {
  background-color: #e2e8f0;
}

.btn-primary {
  background-color: #1e3a8a;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #172554;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
