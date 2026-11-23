<script setup lang="ts">
import { ref, watch } from "vue";
import type { Donor, Grant, RecordDonationPayload } from "@/types/fundraising";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  donors: Donor[];
  grants?: Grant[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: RecordDonationPayload): void;
}>();

const donorId = ref("");
const amount = ref("");
const currency = ref("USD");
const paymentMethod = ref("bank_transfer");
const reference = ref("");
const grantId = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      donorId.value = props.donors[0]?.id || "";
      amount.value = "";
      currency.value = "USD";
      paymentMethod.value = "bank_transfer";
      reference.value = "";
      grantId.value = "";
    }
  }
);

function handleSubmit() {
  if (!donorId.value || !amount.value) return;

  emit("create", {
    donor_id: donorId.value,
    amount: Number(amount.value),
    currency: currency.value,
    payment_method: paymentMethod.value,
    reference: reference.value.trim() || undefined,
    grant_id: grantId.value || null,
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Record Incoming Contribution" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-group">
        <label for="don-donor">Donor Supporter *</label>
        <select id="don-donor" v-model="donorId" class="form-input" required>
          <option value="" disabled>Select Donor</option>
          <option v-for="d in donors" :key="d.id" :value="d.id">
            {{ d.name }} ({{ d.donor_type }})
          </option>
        </select>
      </div>

      <div class="form-row">
        <div class="form-group flex-2">
          <label for="don-amount">Contribution Amount *</label>
          <input
            id="don-amount"
            v-model="amount"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="e.g. 25000.00"
            required
            class="form-input font-mono"
          />
        </div>

        <div class="form-group flex-1">
          <label for="don-curr">Currency</label>
          <select id="don-curr" v-model="currency" class="form-input">
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
            <option value="ETB">ETB</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="don-method">Payment Channel *</label>
          <select id="don-method" v-model="paymentMethod" class="form-input" required>
            <option value="bank_transfer">Direct Bank Transfer</option>
            <option value="cash">Cash / Petty</option>
            <option value="check">Bank Check</option>
            <option value="online">Online / Wire</option>
          </select>
        </div>

        <div class="form-group flex-1">
          <label for="don-ref">Transaction / Check Ref</label>
          <input
            id="don-ref"
            v-model="reference"
            type="text"
            placeholder="e.g. WIRE-849202"
            class="form-input font-mono"
          />
        </div>
      </div>

      <div class="form-group" v-if="grants && grants.length > 0">
        <label for="don-grant">Linked Institutional Grant (Optional)</label>
        <select id="don-grant" v-model="grantId" class="form-input">
          <option value="">None (Unrestricted General Contribution)</option>
          <option v-for="g in grants" :key="g.id" :value="g.id">
            {{ g.title }} ({{ g.reference_code }})
          </option>
        </select>
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
          :disabled="isLoading || !donorId || !amount"
        >
          {{ isLoading ? "Recording..." : "Record Contribution" }}
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

.flex-2 {
  flex: 2;
  min-width: 180px;
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
