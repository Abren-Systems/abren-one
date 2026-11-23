<script setup lang="ts">
import { ref, watch } from "vue";
import type { CreateProjectPayload, Program } from "@/types/program";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  programs: Program[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: CreateProjectPayload): void;
}>();

const programId = ref("");
const name = ref("");
const description = ref("");
const currency = ref("USD");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      programId.value = props.programs[0]?.id || "";
      name.value = "";
      description.value = "";
      currency.value = "USD";
    }
  }
);

function handleSubmit() {
  if (!programId.value || !name.value.trim()) return;

  emit("create", {
    program_id: programId.value,
    name: name.value.trim(),
    description: description.value.trim() || undefined,
    budget_currency: currency.value,
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Create Deliverable Project" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-group">
        <label for="prj-prog">Parent Strategic Program *</label>
        <select id="prj-prog" v-model="programId" class="form-input" required>
          <option value="" disabled>Select Program</option>
          <option v-for="p in programs" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>
      </div>

      <div class="form-row">
        <div class="form-group flex-2">
          <label for="prj-name">Project Name *</label>
          <input
            id="prj-name"
            v-model="name"
            type="text"
            placeholder="e.g. Clean Water Tanker Distribution 2026"
            required
            class="form-input"
          />
        </div>

        <div class="form-group flex-1">
          <label for="prj-curr">Budget Currency</label>
          <select id="prj-curr" v-model="currency" class="form-input">
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
            <option value="ETB">ETB</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label for="prj-desc">Project Description (Optional)</label>
        <textarea
          id="prj-desc"
          v-model="description"
          rows="2"
          placeholder="Scope, operational location, target beneficiary count..."
          class="form-input"
        ></textarea>
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
          :disabled="isLoading || !programId || !name.trim()"
        >
          {{ isLoading ? "Creating..." : "Create Project" }}
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

.form-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.flex-1 {
  flex: 1;
  min-width: 120px;
}

.flex-2 {
  flex: 2;
  min-width: 200px;
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
