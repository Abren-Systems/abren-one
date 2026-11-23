<script setup lang="ts">
import { ref, watch } from "vue";
import type { CreateAccountPayload } from "@/types/finance";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: CreateAccountPayload): void;
}>();

const code = ref("");
const name = ref("");
const accountType = ref<"asset" | "liability" | "equity" | "revenue" | "expense">("asset");
const currency = ref("USD");
const description = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      code.value = "";
      name.value = "";
      accountType.value = "asset";
      currency.value = "USD";
      description.value = "";
    }
  }
);

function handleSubmit() {
  if (!code.value.trim() || !name.value.trim()) return;

  emit("create", {
    code: code.value.trim(),
    name: name.value.trim(),
    account_type: accountType.value,
    currency: currency.value,
    description: description.value.trim(),
  });
}
</script>

<template>
  <ModalDialog :show="open" title="Add Chart of Accounts Record" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-row">
        <div class="form-group flex-1">
          <label for="acc-code">Account Code *</label>
          <input
            id="acc-code"
            v-model="code"
            type="text"
            placeholder="e.g. 1010, 1200, 5100"
            required
            class="form-input font-mono"
          />
        </div>

        <div class="form-group flex-1">
          <label for="acc-type">Classification *</label>
          <select id="acc-type" v-model="accountType" class="form-input" required>
            <option value="asset">Asset (Debit balance)</option>
            <option value="liability">Liability (Credit balance)</option>
            <option value="equity">Equity (Credit balance)</option>
            <option value="revenue">Revenue (Credit balance)</option>
            <option value="expense">Expense (Debit balance)</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label for="acc-name">Account Name *</label>
        <input
          id="acc-name"
          v-model="name"
          type="text"
          placeholder="e.g. Operating Bank Account, Program Relief Inventory"
          required
          class="form-input"
        />
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label for="acc-curr">Currency *</label>
          <select id="acc-curr" v-model="currency" class="form-input">
            <option value="USD">USD - US Dollar</option>
            <option value="EUR">EUR - Euro</option>
            <option value="GBP">GBP - British Pound</option>
            <option value="ETB">ETB - Ethiopian Birr</option>
          </select>
        </div>

        <div class="form-group flex-2">
          <label for="acc-desc">Description (Optional)</label>
          <input
            id="acc-desc"
            v-model="description"
            type="text"
            placeholder="Purpose or restrictions on this account"
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
          :disabled="isLoading || !code.trim() || !name.trim()"
        >
          {{ isLoading ? "Creating..." : "Create Account" }}
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
