<script setup lang="ts">
import { ref, watch } from "vue";
import type { RegisterBeneficiaryPayload } from "@/types/beneficiary";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: RegisterBeneficiaryPayload): void;
}>();

const benType = ref<"individual" | "household" | "community">("individual");
const firstName = ref("");
const lastName = ref("");
const householdName = ref("");
const idNumber = ref("");
const vulnLevel = ref<"low" | "medium" | "high" | "critical">("medium");
const contactPhone = ref("");
const contactAddress = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      benType.value = "individual";
      firstName.value = "";
      lastName.value = "";
      householdName.value = "";
      idNumber.value = "";
      vulnLevel.value = "medium";
      contactPhone.value = "";
      contactAddress.value = "";
    }
  }
);

function handleSubmit() {
  if (benType.value === "household" && !householdName.value.trim()) return;
  if (benType.value !== "household" && (!firstName.value.trim() || !lastName.value.trim())) return;

  emit("create", {
    beneficiary_type: benType.value,
    first_name: benType.value !== "household" ? firstName.value.trim() : undefined,
    last_name: benType.value !== "household" ? lastName.value.trim() : undefined,
    household_name: benType.value === "household" ? householdName.value.trim() : undefined,
    identification_number: idNumber.value.trim() || undefined,
    vulnerability_level: vulnLevel.value,
    contact_phone: contactPhone.value.trim() || undefined,
    contact_address: contactAddress.value.trim() || undefined,
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Register Beneficiary Profile" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-row">
        <div class="form-group flex-1">
          <label for="ben-type">Recipient Type *</label>
          <select id="ben-type" v-model="benType" class="form-input" required>
            <option value="individual">Individual</option>
            <option value="household">Household</option>
            <option value="community">Community / Group</option>
          </select>
        </div>

        <div class="form-group flex-1">
          <label for="ben-vuln">Vulnerability Level *</label>
          <select id="ben-vuln" v-model="vulnLevel" class="form-input" required>
            <option value="low">Low Risk</option>
            <option value="medium">Medium Vulnerability</option>
            <option value="high">High Vulnerability</option>
            <option value="critical">Critical Emergency</option>
          </select>
        </div>
      </div>

      <div v-if="benType === 'household'" class="form-group">
        <label for="hh-name">Household / Family Name *</label>
        <input
          id="hh-name"
          v-model="householdName"
          type="text"
          placeholder="e.g. Warsame Family Household"
          required
          class="form-input"
        />
      </div>

      <div v-else class="form-row">
        <div class="form-group flex-1">
          <label for="first-name">First Name *</label>
          <input
            id="first-name"
            v-model="firstName"
            type="text"
            placeholder="e.g. Halima"
            required
            class="form-input"
          />
        </div>

        <div class="form-group flex-1">
          <label for="last-name">Last Name *</label>
          <input
            id="last-name"
            v-model="lastName"
            type="text"
            placeholder="e.g. Ahmed"
            required
            class="form-input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="id-number">National ID / Ration Card #</label>
          <input
            id="id-number"
            v-model="idNumber"
            type="text"
            placeholder="e.g. ID-8942-A"
            class="form-input font-mono"
          />
        </div>

        <div class="form-group flex-1">
          <label for="contact-phone">Contact Phone</label>
          <input
            id="contact-phone"
            v-model="contactPhone"
            type="tel"
            placeholder="+251 91 123 4567"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="contact-address">Location / Camp / Kebele Address</label>
        <input
          id="contact-address"
          v-model="contactAddress"
          type="text"
          placeholder="e.g. Sector 4, Block B, Dolo Ado Camp"
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
          :disabled="
            isLoading ||
            (benType === 'household' ? !householdName.trim() : !firstName.trim() || !lastName.trim())
          "
        >
          {{ isLoading ? "Registering..." : "Register Beneficiary" }}
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
