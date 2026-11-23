<script setup lang="ts">
import { ref } from "vue";
import type { ItemSummary, PendingGRN, WarehouseSummary } from "@/types/inventory";

interface ReceiveLineForm {
  po_item_id: string;
  item_id: string;
  description: string;
  quantity_accepted: string;
  quantity_remaining: string;
  quantity: string;
  unit_cost: string;
  batch_number: string;
  expiry_date: string;
}

const props = defineProps<{
  show: boolean;
  pendingGrns: PendingGRN[];
  warehouses: WarehouseSummary[];
  items: ItemSummary[];
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    payload: {
      goods_receipt_id: string;
      warehouse_id: string;
      transaction_date: string;
      reference_document: string;
      notes: string;
      lines: {
        po_item_id: string;
        item_id: string;
        quantity: string;
        unit_cost: string;
        batch_number?: string;
        expiry_date?: string;
      }[];
    }
  ): void;
}>();

const selectedGrn = ref<PendingGRN | null>(null);
const form = ref({
  goods_receipt_id: "",
  warehouse_id: "",
  transaction_date: new Date().toISOString().split("T")[0],
  reference_document: "",
  notes: "",
  lines: [] as ReceiveLineForm[],
});

function onSelectPendingGrn(grnId: string): void {
  form.value.goods_receipt_id = grnId;
  selectedGrn.value = props.pendingGrns.find((g) => g.grn_id === grnId) || null;

  if (selectedGrn.value) {
    form.value.reference_document = selectedGrn.value.receipt_number;
    form.value.lines = selectedGrn.value.items
      .filter((it) => Number(it.quantity_remaining) > 0)
      .map((it) => {
        const matchingCatalogItem = props.items.find(
          (catalog) =>
            catalog.name.toLowerCase() === it.description.toLowerCase() ||
            it.description.toLowerCase().includes(catalog.name.toLowerCase())
        );
        return {
          po_item_id: it.po_item_id,
          item_id: matchingCatalogItem ? matchingCatalogItem.id : "",
          description: it.description,
          quantity_accepted: it.quantity_accepted,
          quantity_remaining: it.quantity_remaining,
          quantity: it.quantity_remaining,
          unit_cost: it.unit_price,
          batch_number: "",
          expiry_date: "",
        };
      });
  } else {
    form.value.lines = [];
  }
}

function onSubmit(): void {
  emit("submit", {
    goods_receipt_id: form.value.goods_receipt_id,
    warehouse_id: form.value.warehouse_id,
    transaction_date: form.value.transaction_date,
    reference_document: form.value.reference_document,
    notes: form.value.notes,
    lines: form.value.lines.map((l) => ({
      po_item_id: l.po_item_id,
      item_id: l.item_id,
      quantity: l.quantity,
      unit_cost: l.unit_cost,
      batch_number: l.batch_number || undefined,
      expiry_date: l.expiry_date || undefined,
    })),
  });
}
</script>

<template>
  <div v-if="show" class="modal-backdrop">
    <div class="modal-card modal-lg">
      <h3>Receive Purchased Stock from Procurement GRN</h3>
      <p class="modal-subtitle">
        Intake inspected and accepted items from a Goods Receipt Note into warehouse stock balances.
      </p>

      <form @submit.prevent="onSubmit">
        <div class="form-row">
          <div class="form-group">
            <label>Select Pending Goods Receipt *</label>
            <select
              class="form-select"
              :value="form.goods_receipt_id"
              required
              @change="onSelectPendingGrn(($event.target as HTMLSelectElement).value)"
            >
              <option value="">-- Choose Inspected GRN --</option>
              <option v-for="g in pendingGrns" :key="g.grn_id" :value="g.grn_id">
                {{ g.receipt_number }} — PO: {{ g.purchase_order_number }} ({{ g.vendor_name }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Destination Warehouse *</label>
            <select v-model="form.warehouse_id" required class="form-select">
              <option value="">Select Warehouse</option>
              <option v-for="w in warehouses" :key="w.id" :value="w.id">
                {{ w.name }} ({{ w.code }})
              </option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Transaction Date *</label>
            <input v-model="form.transaction_date" type="date" required class="form-input" />
          </div>
          <div class="form-group">
            <label>Reference Document</label>
            <input
              v-model="form.reference_document"
              type="text"
              placeholder="e.g. GRN-001 or Delivery Note"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-group">
          <label>Notes / Inspection Remarks</label>
          <input
            v-model="form.notes"
            type="text"
            placeholder="Optional receiving notes..."
            class="form-input"
          />
        </div>

        <!-- GRN Line Items Mapping -->
        <div v-if="selectedGrn" class="lines-section">
          <h4>Accepted Items to Receive</h4>
          <div v-if="form.lines.length === 0" class="empty-state">
            No accepted lines remaining to receive for this receipt.
          </div>

          <div
            v-for="(line, idx) in form.lines"
            :key="line.po_item_id"
            class="line-item-box"
          >
            <div class="line-header">
              <span>Line {{ idx + 1 }}: {{ line.description }}</span>
              <span class="line-meta">
                Accepted: {{ line.quantity_accepted }} | Remaining: <strong>{{ line.quantity_remaining }}</strong>
              </span>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Map to Catalog Item *</label>
                <select v-model="line.item_id" required class="form-select">
                  <option value="">-- Select Item --</option>
                  <option v-for="it in items" :key="it.id" :value="it.id">
                    {{ it.name }} ({{ it.item_code }})
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Quantity to Receive *</label>
                <input
                  v-model="line.quantity"
                  type="number"
                  step="0.01"
                  min="0.01"
                  :max="line.quantity_remaining"
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>Unit Cost</label>
                <input
                  v-model="line.unit_cost"
                  type="number"
                  step="0.01"
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Batch / Lot # (if applicable)</label>
                <input
                  v-model="line.batch_number"
                  type="text"
                  placeholder="e.g. LOT-2026-A"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>Expiry Date (if applicable)</label>
                <input
                  v-model="line.expiry_date"
                  type="date"
                  class="form-input"
                />
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state-card">
          Please select an inspected Goods Receipt Note above to view and map its line items.
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-ghost" @click="emit('close')">
            Cancel
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="isLoading || !selectedGrn || form.lines.length === 0"
          >
            Post Stock Receipt
          </button>
        </div>
      </form>
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
  max-width: 520px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-lg {
  max-width: 760px;
}

.modal-subtitle {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  margin: -0.5rem 0 0.5rem 0;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.form-input,
.form-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.875rem;
}

.lines-section {
  margin-top: 1rem;
  border-top: 1px solid var(--color-border);
  padding-top: 1rem;
}

.lines-section h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.9375rem;
}

.line-item-box {
  border-bottom: 1px solid var(--color-border);
  padding: 0.75rem 0;
  margin-bottom: 0.75rem;
}

.line-header {
  font-weight: 600;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
}

.line-meta {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.875rem;
  padding: 1rem;
}

.empty-state-card {
  padding: 1.5rem;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
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

.btn-ghost {
  background: transparent;
  color: var(--color-text-muted);
}
</style>
