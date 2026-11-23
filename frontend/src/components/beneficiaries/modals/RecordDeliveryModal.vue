<script setup lang="ts">
import { ref, watch } from "vue";
import type { Beneficiary, RecordDeliveryPayload } from "@/types/beneficiary";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  beneficiaries: Beneficiary[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: RecordDeliveryPayload): void;
}>();

const beneficiaryId = ref("");
const serviceType = ref("food_assistance");
const deliveryDate = ref(new Date().toISOString().split("T")[0]);
const quantity = ref("1.00");
const unit = ref("kits");
const notes = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      beneficiaryId.value = props.beneficiaries[0]?.id || "";
      serviceType.value = "food_assistance";
      deliveryDate.value = new Date().toISOString().split("T")[0];
      quantity.value = "1.00";
      unit.value = "kits";
      notes.value = "";
    }
  }
);

function handleSubmit() {
  if (!beneficiaryId.value || !deliveryDate.value || !quantity.value || !unit.value.trim()) return;

  emit("create", {
    beneficiary_id: beneficiaryId.value,
    service_type: serviceType.value,
    delivery_date: deliveryDate.value,
    quantity: Number(quantity.value),
    unit: unit.value.trim(),
    notes: notes.value.trim() || undefined,
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Record Aid Distribution Event" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-group">
        <label for="del-ben">Recipient Beneficiary *</label>
        <select id="del-ben" v-model="beneficiaryId" class="form-input" required>
          <option value="" disabled>Select Recipient</option>
          <option v-for="b in beneficiaries" :key="b.id" :value="b.id">
            {{ b.display_name }} ({{ b.beneficiary_type }} - {{ b.vulnerability_level }})
          </option>
        </select>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="del-type">Service / Aid Modality *</label>
          <select id="del-type" v-model="serviceType" class="form-input" required>
            <option value="food_assistance">Food Assistance</option>
            <option value="medical_support">Medical Support</option>
            <option value="cash_transfer">Cash Transfer</option>
            <option value="education_training">Education & Training</option>
            <option value="shelter_wash">Shelter / WASH</option>
            <option value="legal_advocacy">Legal Advocacy</option>
            <option value="other">Other Humanitarian Aid</option>
          </select>
        </div>

        <div class="form-group flex-1">
          <label for="del-date">Delivery Date *</label>
          <input
            id="del-date"
            v-model="deliveryDate"
            type="date"
            required
            class="form-input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="del-qty">Disbursed Quantity *</label>
          <input
            id="del-qty"
            v-model="quantity"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="e.g. 5.00"
            required
            class="form-input font-mono"
          />
        </div>

        <div class="form-group flex-1">
          <label for="del-unit">Unit of Measure *</label>
          <input
            id="del-unit"
            v-model="unit"
            type="text"
            placeholder="e.g. rations, kits, MT, USD"
            required
            class="form-input"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="del-notes">Distribution Notes / Waybill #</label>
        <input
          id="del-notes"
          v-model="notes"
          type="text"
          placeholder="e.g. Verification verified with fingerprint / ration token"
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
          :disabled="isLoading || !beneficiaryId || !quantity || !unit.trim()"
        >
          {{ isLoading ? "Recording..." : "Record Distribution" }}
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
