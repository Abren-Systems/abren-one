<script setup lang="ts">
import { ref, watch } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";
import type { PurchaseOrder } from "@/types/procurement";

const props = defineProps<{
  show: boolean;
  order: PurchaseOrder | null;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    payload: {
      purchase_order_id: string;
      received_date: string;
      receipt_type: "goods" | "services";
      inspection_notes: string;
      items: Array<{
        po_item_id: string;
        quantity_received: number;
      }>;
    }
  ): void;
}>();

const receiptDate = ref(new Date().toISOString().split("T")[0]);
const receiptType = ref<"goods" | "services">("goods");
const inspectionNotes = ref("");

interface ReceiptLine {
  po_item_id: string;
  description: string;
  quantity_received: number;
}

const lines = ref<ReceiptLine[]>([]);

watch(
  () => props.show,
  (isShown) => {
    if (isShown && props.order) {
      receiptDate.value = new Date().toISOString().split("T")[0];
      receiptType.value = "goods";
      inspectionNotes.value = "";
      lines.value = (props.order.items || []).map((it) => ({
        po_item_id: it.id,
        description: it.description,
        quantity_received: Number(it.quantity_outstanding || it.quantity),
      }));
    }
  }
);

function onSubmit() {
  if (!props.order || lines.value.length === 0) return;
  emit("submit", {
    purchase_order_id: props.order.id,
    received_date: receiptDate.value,
    receipt_type: receiptType.value,
    inspection_notes: inspectionNotes.value.trim(),
    items: lines.value.map((l) => ({
      po_item_id: l.po_item_id,
      quantity_received: Number(l.quantity_received),
    })),
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Record Delivery Receipt (GRN)"
    max-width="640px"
    @close="emit('close')"
  >
    <form id="record-grn-form" @submit.prevent="onSubmit">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Received Date</label>
          <input v-model="receiptDate" type="date" required class="form-input" />
        </div>
        <div class="form-group">
          <label class="form-label">Receipt Type</label>
          <select v-model="receiptType" class="form-select">
            <option value="goods">Physical Goods</option>
            <option value="services">Service Completion</option>
          </select>
        </div>
      </div>

      <div class="lines-section">
        <h4 class="section-title">Received Quantities</h4>
        <div v-for="(line, idx) in lines" :key="idx" class="line-row">
          <div class="line-desc">{{ line.description }}</div>
          <input
            v-model.number="line.quantity_received"
            type="number"
            min="0"
            required
            placeholder="Count received"
            class="form-input line-input"
          />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Delivery / Waybill Notes</label>
        <textarea
          v-model="inspectionNotes"
          rows="2"
          placeholder="Carrier details, condition on arrival..."
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
        form="record-grn-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Save Goods Receipt
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

.lines-section {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin: 1rem 0;
  background-color: #fafbfc;
}

.section-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.9375rem;
  font-weight: 600;
}

.line-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.line-desc {
  flex: 2;
  font-size: 0.875rem;
  color: var(--color-text);
}

.line-input {
  flex: 1;
  max-width: 140px;
}
</style>
