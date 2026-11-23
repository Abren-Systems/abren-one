<script setup lang="ts">
import { ref, watch } from "vue";
import type { CreateDepartmentPayload } from "@/api/modules/organizations";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: CreateDepartmentPayload): void;
}>();

const name = ref("");
const code = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      name.value = "";
      code.value = "";
    }
  }
);

function handleSubmit() {
  if (!name.value.trim() || !code.value.trim()) return;

  emit("create", {
    name: name.value.trim(),
    code: code.value.trim().toUpperCase(),
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Add Functional Department" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-group">
        <label for="dept-name">Department Name *</label>
        <input
          id="dept-name"
          v-model="name"
          type="text"
          placeholder="e.g. Logistics & Supply Chain"
          required
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label for="dept-code">Department Code *</label>
        <input
          id="dept-code"
          v-model="code"
          type="text"
          placeholder="e.g. LOG"
          required
          class="form-input"
        />
        <span class="field-hint">Short uppercase identifier (e.g. FIN, HR, OPS, LOG)</span>
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
          :disabled="isLoading || !name.trim() || !code.trim()"
        >
          {{ isLoading ? "Adding..." : "Add Department" }}
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

.field-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
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
