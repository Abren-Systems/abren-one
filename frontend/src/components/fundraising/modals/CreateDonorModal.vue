<script setup lang="ts">
import { ref, watch } from "vue";
import type { CreateDonorPayload } from "@/types/fundraising";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: CreateDonorPayload): void;
}>();

const name = ref("");
const donorType = ref("foundation");
const email = ref("");
const phone = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      name.value = "";
      donorType.value = "foundation";
      email.value = "";
      phone.value = "";
    }
  }
);

function handleSubmit() {
  if (!name.value.trim()) return;

  emit("create", {
    name: name.value.trim(),
    donor_type: donorType.value,
    email: email.value.trim() || undefined,
    phone: phone.value.trim() || undefined,
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Add Supporter / Donor" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-group">
        <label for="donor-name">Donor Name *</label>
        <input
          id="donor-name"
          v-model="name"
          type="text"
          placeholder="e.g. Global Humanitarian Foundation"
          required
          class="form-input"
        />
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="donor-type">Donor Classification *</label>
          <select id="donor-type" v-model="donorType" class="form-input" required>
            <option value="foundation">Foundation</option>
            <option value="individual">Individual Supporter</option>
            <option value="corporation">Corporation / CSR</option>
            <option value="government">Government / Multilateral</option>
          </select>
        </div>

        <div class="form-group flex-1">
          <label for="donor-phone">Phone Number</label>
          <input
            id="donor-phone"
            v-model="phone"
            type="tel"
            placeholder="+1 (555) 000-0000"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="donor-email">Official Contact Email</label>
        <input
          id="donor-email"
          v-model="email"
          type="email"
          placeholder="grants@foundation.org"
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
          :disabled="isLoading || !name.trim()"
        >
          {{ isLoading ? "Adding..." : "Add Supporter" }}
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
  min-width: 140px;
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
