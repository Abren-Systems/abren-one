<script setup lang="ts">
import { ref, computed, watch } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";

interface ReqFormLine {
  description: string;
  quantity: number;
  unit: string;
  estimated_unit_price: number;
}

const props = defineProps<{
  show: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    payload: {
      title: string;
      currency: string;
      notes: string;
      items: Array<{
        description: string;
        quantity: number;
        unit: string;
        estimated_unit_price: number;
      }>;
    }
  ): void;
}>();

const title = ref("");
const currency = ref("USD");
const notes = ref("");
const lines = ref<ReqFormLine[]>([
  { description: "", quantity: 1, unit: "each", estimated_unit_price: 0 },
]);

function addLine() {
  lines.value.push({ description: "", quantity: 1, unit: "each", estimated_unit_price: 0 });
}

function removeLine(idx: number) {
  if (lines.value.length > 1) {
    lines.value.splice(idx, 1);
  }
}

const estimatedTotal = computed(() => {
  return lines.value.reduce(
    (acc, l) => acc + (Number(l.quantity) || 0) * (Number(l.estimated_unit_price) || 0),
    0
  );
});

watch(
  () => props.show,
  (isShown) => {
    if (isShown) {
      title.value = "";
      currency.value = "USD";
      notes.value = "";
      lines.value = [{ description: "", quantity: 1, unit: "each", estimated_unit_price: 0 }];
    }
  }
);

function onSubmit() {
  if (!title.value.trim() || lines.value.length === 0) return;
  emit("submit", {
    title: title.value.trim(),
    currency: currency.value.trim().toUpperCase(),
    notes: notes.value.trim(),
    items: lines.value.map((l) => ({
      description: l.description.trim(),
      quantity: Number(l.quantity),
      unit: l.unit.trim(),
      estimated_unit_price: Number(l.estimated_unit_price),
    })),
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Raise Purchase Requisition"
    max-width="640px"
    @close="emit('close')"
  >
    <form id="create-req-form" @submit.prevent="onSubmit">
      <div class="form-group">
        <label class="form-label">Requisition Title / Purpose</label>
        <input
          v-model="title"
          type="text"
          required
          placeholder="e.g. Q1 Dormitory Food Supplies"
          class="form-input"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Currency</label>
          <input
            v-model="currency"
            type="text"
            maxlength="3"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Estimated Total</label>
          <div class="static-total font-mono font-bold">
            {{ currency }} {{ estimatedTotal.toFixed(2) }}
          </div>
        </div>
      </div>

      <div class="lines-section">
        <div class="lines-header">
          <h4>Line Items</h4>
          <button type="button" class="btn btn-secondary btn-xs" @click="addLine">
            + Add Item
          </button>
        </div>

        <div v-for="(line, idx) in lines" :key="idx" class="line-row">
          <input
            v-model="line.description"
            type="text"
            required
            placeholder="Item description"
            class="form-input flex-2"
          />
          <input
            v-model.number="line.quantity"
            type="number"
            min="1"
            required
            placeholder="Qty"
            class="form-input flex-1"
          />
          <input
            v-model="line.unit"
            type="text"
            required
            placeholder="Unit"
            class="form-input flex-1"
          />
          <input
            v-model.number="line.estimated_unit_price"
            type="number"
            min="0"
            step="0.01"
            placeholder="Est. Price"
            class="form-input flex-1"
          />
          <button
            v-if="lines.length > 1"
            type="button"
            class="btn-remove"
            @click="removeLine(idx)"
          >
            ✕
          </button>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Notes & Justification</label>
        <textarea
          v-model="notes"
          rows="2"
          placeholder="Program activity context, justification..."
          class="form-textarea"
        ></textarea>
      </div>
    </form>

    <template #footer>
      <button
        type="button"
        class="btn btn-secondary"
        @click="emit('close')"
      >
        Cancel
      </button>
      <button
        type="submit"
        form="create-req-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Create Requisition
      </button>
    </template>
  </ModalDialog>
</template>

<style scoped>
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.static-total {
  padding: 0.5rem 0.75rem;
  background-color: #f8fafc;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.9375rem;
  color: var(--color-primary);
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: 700;
}

.lines-section {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin: 1rem 0;
  background-color: #fafbfc;
}

.lines-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.lines-header h4 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text);
}

.line-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.flex-2 {
  flex: 2;
}

.flex-1 {
  flex: 1;
}

.btn-remove {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.btn-xs {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
}
</style>
