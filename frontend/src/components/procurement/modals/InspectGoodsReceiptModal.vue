<script setup lang="ts">
import { ref, watch } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";
import type { GoodsReceiptNote } from "@/types/procurement";

interface InspectionLine {
  grn_item_id: string;
  description: string;
  quantity_received: number;
  quantity_accepted: number;
  quantity_rejected: number;
  rejection_reason: string;
}

const props = defineProps<{
  show: boolean;
  grn: GoodsReceiptNote | null;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    payload: {
      grnId: string;
      inspections: Array<{
        grn_item_id: string;
        quantity_accepted: number;
        quantity_rejected: number;
        rejection_reason?: string;
      }>;
    }
  ): void;
}>();

const lines = ref<InspectionLine[]>([]);

watch(
  () => props.show,
  (isShown) => {
    if (isShown && props.grn) {
      lines.value = (props.grn.items || []).map((item) => ({
        grn_item_id: item.id,
        description: item.description || "PO Line Item",
        quantity_received: Number(item.quantity_received),
        quantity_accepted: Number(item.quantity_received),
        quantity_rejected: 0,
        rejection_reason: "",
      }));
    }
  }
);

function onSubmit() {
  if (!props.grn || lines.value.length === 0) return;
  emit("submit", {
    grnId: props.grn.id,
    inspections: lines.value.map((l) => ({
      grn_item_id: l.grn_item_id,
      quantity_accepted: Number(l.quantity_accepted),
      quantity_rejected: Number(l.quantity_rejected),
      rejection_reason: l.rejection_reason.trim() || undefined,
    })),
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    :title="`Inspection & Reconciliation — ${grn?.receipt_number || ''}`"
    max-width="740px"
    @close="emit('close')"
  >
    <form id="inspect-grn-form" @submit.prevent="onSubmit">
      <p class="inspection-hint">
        Accepted + Rejected quantities must exactly equal the received physical count.
      </p>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Item</th>
              <th class="text-right">Received</th>
              <th class="text-right">Accepted</th>
              <th class="text-right">Rejected</th>
              <th>Rejection Reason</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(line, idx) in lines" :key="idx">
              <td>{{ line.description }}</td>
              <td class="text-right font-mono font-bold">
                {{ line.quantity_received }}
              </td>
              <td class="text-right">
                <input
                  v-model.number="line.quantity_accepted"
                  type="number"
                  min="0"
                  :max="line.quantity_received"
                  required
                  class="form-input qty-input"
                />
              </td>
              <td class="text-right">
                <input
                  v-model.number="line.quantity_rejected"
                  type="number"
                  min="0"
                  :max="line.quantity_received"
                  required
                  class="form-input qty-input"
                />
              </td>
              <td>
                <input
                  v-model="line.rejection_reason"
                  type="text"
                  placeholder="Required if rejected"
                  class="form-input"
                  :required="line.quantity_rejected > 0"
                />
              </td>
            </tr>
          </tbody>
        </table>
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
        form="inspect-grn-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Finalize Inspection
      </button>
    </template>
  </ModalDialog>
</template>

<style scoped>
.inspection-hint {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0 0 1rem 0;
}

.table-container {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th,
.data-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: var(--color-text-muted);
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: 700;
}

.text-right {
  text-align: right;
}

.qty-input {
  max-width: 80px;
  text-align: right;
}
</style>
