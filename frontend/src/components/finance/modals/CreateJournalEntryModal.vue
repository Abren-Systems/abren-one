<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { Account, CreateJournalEntryPayload } from "@/types/finance";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  accounts: Account[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "create", payload: CreateJournalEntryPayload): void;
}>();

const entryDate = ref(new Date().toISOString().split("T")[0]);
const memo = ref("");
const currency = ref("USD");
const postImmediately = ref(true);

interface FormLine {
  account_id: string;
  debit: number;
  credit: number;
  memo: string;
}

const lines = ref<FormLine[]>([
  { account_id: "", debit: 0, credit: 0, memo: "" },
  { account_id: "", debit: 0, credit: 0, memo: "" },
]);

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      entryDate.value = new Date().toISOString().split("T")[0];
      memo.value = "";
      currency.value = "USD";
      postImmediately.value = true;
      lines.value = [
        {
          account_id: props.accounts[0]?.id || "",
          debit: 0,
          credit: 0,
          memo: "",
        },
        {
          account_id: props.accounts[1]?.id || "",
          debit: 0,
          credit: 0,
          memo: "",
        },
      ];
    }
  }
);

const lineTotalDebits = computed(() => {
  return lines.value.reduce((acc, l) => acc + (Number(l.debit) || 0), 0);
});

const lineTotalCredits = computed(() => {
  return lines.value.reduce((acc, l) => acc + (Number(l.credit) || 0), 0);
});

const isFormBalanced = computed(() => {
  return (
    lineTotalDebits.value > 0 &&
    Math.abs(lineTotalDebits.value - lineTotalCredits.value) < 0.001
  );
});

function addLine() {
  lines.value.push({ account_id: "", debit: 0, credit: 0, memo: "" });
}

function removeLine(index: number) {
  if (lines.value.length > 2) {
    lines.value.splice(index, 1);
  }
}

function handleSubmit() {
  if (!isFormBalanced.value || !memo.value.trim()) return;

  emit("create", {
    entry_date: entryDate.value,
    memo: memo.value.trim(),
    currency: currency.value,
    post_immediately: postImmediately.value,
    lines: lines.value.map((l) => ({
      account_id: l.account_id,
      debit: Number(l.debit) || 0,
      credit: Number(l.credit) || 0,
      memo: l.memo.trim(),
    })),
  });
}
</script>

<template>
  <ModalDialog
    :show="open"
    title="Record Balanced Journal Entry"
    @close="emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="modal-form">
      <div class="form-row">
        <div class="form-group flex-1">
          <label for="je-date">Date *</label>
          <input
            id="je-date"
            v-model="entryDate"
            type="date"
            required
            class="form-input"
          />
        </div>

        <div class="form-group flex-2">
          <label for="je-memo">Memo / Purpose *</label>
          <input
            id="je-memo"
            v-model="memo"
            type="text"
            placeholder="e.g. Allocation for emergency relief supplies"
            required
            class="form-input"
          />
        </div>

        <div class="form-group flex-1">
          <label for="je-curr">Currency</label>
          <select id="je-curr" v-model="currency" class="form-input">
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
            <option value="ETB">ETB</option>
          </select>
        </div>
      </div>

      <div class="legs-section">
        <div class="legs-header">
          <span class="legs-title">Entry Legs (Double-Entry Balancing)</span>
          <button
            type="button"
            class="btn btn-sm btn-secondary"
            @click="addLine"
          >
            + Add Leg
          </button>
        </div>

        <div class="legs-table-wrapper">
          <div
            v-for="(line, idx) in lines"
            :key="idx"
            class="line-row"
          >
            <div class="line-col account-col">
              <select
                v-model="line.account_id"
                class="form-input line-select"
                required
              >
                <option value="" disabled>Select Account</option>
                <option
                  v-for="acc in accounts"
                  :key="acc.id"
                  :value="acc.id"
                >
                  {{ acc.code }} - {{ acc.name }} ({{ acc.account_type }})
                </option>
              </select>
            </div>

            <div class="line-col amount-col">
              <input
                v-model.number="line.debit"
                type="number"
                step="0.01"
                min="0"
                placeholder="Debit"
                class="form-input font-mono text-right"
                @focus="line.credit = 0"
              />
            </div>

            <div class="line-col amount-col">
              <input
                v-model.number="line.credit"
                type="number"
                step="0.01"
                min="0"
                placeholder="Credit"
                class="form-input font-mono text-right"
                @focus="line.debit = 0"
              />
            </div>

            <div class="line-col memo-col">
              <input
                v-model="line.memo"
                type="text"
                placeholder="Line memo"
                class="form-input"
              />
            </div>

            <button
              type="button"
              class="btn-icon"
              :disabled="lines.length <= 2"
              title="Remove leg"
              @click="removeLine(idx)"
            >
              ✕
            </button>
          </div>
        </div>

        <div
          class="balance-summary"
          :class="{ balanced: isFormBalanced, unbalanced: !isFormBalanced }"
        >
          <span>
            Total Debits:
            <strong>{{ lineTotalDebits.toFixed(2) }} {{ currency }}</strong>
          </span>
          <span>
            Total Credits:
            <strong>{{ lineTotalCredits.toFixed(2) }} {{ currency }}</strong>
          </span>
          <span class="balance-pill">
            {{ isFormBalanced ? "✓ Balanced" : "⚠️ Unbalanced" }}
          </span>
        </div>
      </div>

      <div class="options-row">
        <label class="checkbox-label">
          <input
            v-model="postImmediately"
            type="checkbox"
          />
          <span>Post immediately to General Ledger (Authoritative)</span>
        </label>
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
          :disabled="isLoading || !isFormBalanced || !memo.trim()"
        >
          {{ isLoading ? "Recording..." : "Record Entry" }}
        </button>
      </div>
    </form>
  </ModalDialog>
</template>

<style scoped>
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 720px;
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
  min-width: 220px;
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

.text-right {
  text-align: right;
}

.legs-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.legs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.legs-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
}

.legs-table-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.line-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr 36px;
  gap: 0.5rem;
  align-items: center;
}

.line-select {
  font-size: 0.8125rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-icon:hover:not(:disabled) {
  background-color: #fee2e2;
  color: #991b1b;
  border-color: #fecaca;
}

.btn-icon:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.balance-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  margin-top: 0.25rem;
}

.balance-summary.balanced {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.balance-summary.unbalanced {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.balance-pill {
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.options-row {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
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

.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
}

.btn-secondary {
  background-color: #ffffff;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.btn-secondary:hover {
  background-color: #f1f5f9;
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
