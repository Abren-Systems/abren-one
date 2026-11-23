<script setup lang="ts">
import { ref, watch } from "vue";
import type { CreateGrantPayload, Donor } from "@/types/fundraising";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  donors: Donor[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: CreateGrantPayload): void;
}>();

const donorId = ref("");
const title = ref("");
const referenceCode = ref("");
const totalAmount = ref("");
const currency = ref("USD");
const startDate = ref(new Date().toISOString().split("T")[0]);
const endDate = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      donorId.value = props.donors[0]?.id || "";
      title.value = "";
      referenceCode.value = "";
      totalAmount.value = "";
      currency.value = "USD";
      startDate.value = new Date().toISOString().split("T")[0];
      endDate.value = "";
    }
  }
);

function handleSubmit() {
  if (!donorId.value || !title.value.trim() || !referenceCode.value.trim() || !totalAmount.value || !startDate.value || !endDate.value) {
    return;
  }

  emit("create", {
    donor_id: donorId.value,
    title: title.value.trim(),
    reference_code: referenceCode.value.trim(),
    total_amount: Number(totalAmount.value),
    currency: currency.value,
    start_date: startDate.value,
    end_date: endDate.value,
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Register Institutional Grant" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-group">
        <label for="grant-donor">Funding Supporter / Donor *</label>
        <select id="grant-donor" v-model="donorId" class="form-input" required>
          <option value="" disabled>Select Donor</option>
          <option v-for="d in donors" :key="d.id" :value="d.id">
            {{ d.name }} ({{ d.donor_type }})
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="grant-title">Grant Agreement Title *</label>
        <input
          id="grant-title"
          v-model="title"
          type="text"
          placeholder="e.g. Emergency Food Security Window 2026"
          required
          class="form-input"
        />
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="grant-ref">Reference Code *</label>
          <input
            id="grant-ref"
            v-model="referenceCode"
            type="text"
            placeholder="e.g. GR-2026-ECHO-01"
            required
            class="form-input font-mono"
          />
        </div>

        <div class="form-group flex-1">
          <label for="grant-amount">Total Commitment *</label>
          <input
            id="grant-amount"
            v-model="totalAmount"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="e.g. 500000.00"
            required
            class="form-input font-mono"
          />
        </div>

        <div class="form-group curr-group">
          <label for="grant-curr">Currency</label>
          <select id="grant-curr" v-model="currency" class="form-input">
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
            <option value="ETB">ETB</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="grant-start">Start Date *</label>
          <input
            id="grant-start"
            v-model="startDate"
            type="date"
            required
            class="form-input"
          />
        </div>

        <div class="form-group flex-1">
          <label for="grant-end">End Date *</label>
          <input
            id="grant-end"
            v-model="endDate"
            type="date"
            required
            class="form-input"
          />
        </div>
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
          :disabled="isLoading || !donorId || !title.trim() || !referenceCode.trim() || !totalAmount || !startDate || !endDate"
        >
          {{ isLoading ? "Registering..." : "Register Grant" }}
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

.curr-group {
  width: 90px;
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

.font-mono {
  font-family: monospace;
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
