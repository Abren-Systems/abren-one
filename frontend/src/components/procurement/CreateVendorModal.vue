<script setup lang="ts">
import { ref } from "vue";

defineProps<{
  show: boolean;
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    payload: {
      name: string;
      vendor_type: string;
      tax_id: string;
      default_payment_terms: string;
      contact_name: string;
      email: string;
    }
  ): void;
}>();

const vendorName = ref("");
const vendorType = ref("goods");
const vendorTaxId = ref("");
const vendorTerms = ref("Net 30");
const vendorContact = ref("");
const vendorEmail = ref("");

function onSubmit(): void {
  emit("submit", {
    name: vendorName.value,
    vendor_type: vendorType.value,
    tax_id: vendorTaxId.value,
    default_payment_terms: vendorTerms.value,
    contact_name: vendorContact.value,
    email: vendorEmail.value,
  });
}
</script>

<template>
  <div v-if="show" class="modal-backdrop">
    <div class="modal-card">
      <div class="modal-header">
        <h3>Add New Supplier / Vendor</h3>
        <button class="modal-close" @click="emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-row">
          <div class="form-group flex-2">
            <label>Vendor Name</label>
            <input v-model="vendorName" type="text" placeholder="e.g. Acme Pharmaceuticals Ltd" />
          </div>
          <div class="form-group flex-1">
            <label>Classification</label>
            <select v-model="vendorType">
              <option value="goods">Goods Supplier</option>
              <option value="services">Service Contractor</option>
              <option value="consulting">Professional Consulting</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group flex-1">
            <label>Tax ID / Registration</label>
            <input v-model="vendorTaxId" type="text" placeholder="TIN / VAT" />
          </div>
          <div class="form-group flex-1">
            <label>Default Terms</label>
            <input v-model="vendorTerms" type="text" placeholder="e.g. Net 30" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group flex-1">
            <label>Contact Person</label>
            <input v-model="vendorContact" type="text" />
          </div>
          <div class="form-group flex-1">
            <label>Email</label>
            <input v-model="vendorEmail" type="email" />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn btn-primary" :disabled="isLoading || !vendorName" @click="onSubmit">
          Save Supplier
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  max-width: 580px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--color-text-muted);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.flex-1 {
  flex: 1;
}

.flex-2 {
  flex: 2;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.form-group input,
.form-group select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.875rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text);
}
</style>
