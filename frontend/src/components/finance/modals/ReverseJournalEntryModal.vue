<script setup lang="ts">
import { ref, watch } from "vue";
import type { JournalEntry } from "@/types/finance";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  open: boolean;
  entry: JournalEntry | null;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "confirm", entryId: string, reason: string): void;
}>();

const reason = ref("");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      reason.value = "";
    }
  }
);

function handleSubmit() {
  if (!props.entry || !reason.value.trim()) return;
  emit("confirm", props.entry.id, reason.value.trim());
}
</script>

<template>
  <ModalDialog
    :show="open"
    title="Reverse Journal Entry"
    @close="emit('close')"
  >
    <div v-if="entry" class="reverse-content">
      <div class="warning-callout">
        <span class="warning-icon">⚠️</span>
        <div class="warning-text">
          <strong>Accounting Principle:</strong> Posted journal entries are immutable and cannot be edited or deleted. Reversing creates a linked offsetting entry that offsets all debits and credits.
        </div>
      </div>

      <div class="entry-summary">
        <div class="summary-row">
          <span class="summary-label">Entry Number:</span>
          <span class="font-mono font-bold">{{ entry.entry_number }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Date:</span>
          <span>{{ entry.entry_date }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Amount:</span>
          <span class="font-bold">{{ entry.total_amount }} {{ entry.currency }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Original Memo:</span>
          <span>{{ entry.memo }}</span>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="rev-reason">Reversal Reason / Justification *</label>
          <textarea
            id="rev-reason"
            v-model="reason"
            rows="3"
            placeholder="Explain why this entry is being reversed (e.g. Inadvertent duplicate entry, incorrect coding)"
            required
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
            class="btn btn-danger"
            :disabled="isLoading || !reason.trim()"
          >
            {{ isLoading ? "Reversing..." : "Confirm Reversal" }}
          </button>
        </div>
      </form>
    </div>
  </ModalDialog>
</template>

<style scoped>
.reverse-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.warning-callout {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 6px;
  color: #92400e;
  font-size: 0.8125rem;
  line-height: 1.4;
}

.warning-icon {
  font-size: 1.1rem;
}

.entry-summary {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  color: #64748b;
  font-weight: 500;
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: 700;
}

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

.form-input {
  padding: 0.55rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: #ffffff;
  color: #0f172a;
  resize: vertical;
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

.btn-danger {
  background-color: #dc2626;
  color: #ffffff;
}

.btn-danger:hover {
  background-color: #b91c1c;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
