<script setup lang="ts">
import { ref, watch } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";
import type { PurchaseRequisition, Vendor } from "@/types/procurement";

interface OrderFormLine {
  description: string;
  quantity: number;
  unit: string;
  unit_price: number;
  requisition_item_id?: string;
}

const props = defineProps<{
  show: boolean;
  vendors: Vendor[];
  requisitions: PurchaseRequisition[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    payload: {
      vendor_id: string;
      requisition_id?: string | null;
      currency: string;
      expected_delivery_date?: string | null;
      delivery_address?: string;
      notes?: string;
      items: Array<{
        description: string;
        quantity: number;
        unit: string;
        unit_price: number;
      }>;
    }
  ): void;
}>();

const vendorId = ref("");
const requisitionId = ref("");
const currency = ref("USD");
const deliveryDate = ref("");
const deliveryAddress = ref("");
const notes = ref("");
const lines = ref<OrderFormLine[]>([
  { description: "", quantity: 1, unit: "each", unit_price: 0 },
]);

function addLine() {
  lines.value.push({ description: "", quantity: 1, unit: "each", unit_price: 0 });
}

function removeLine(idx: number) {
  if (lines.value.length > 1) {
    lines.value.splice(idx, 1);
  }
}

watch(
  () => props.show,
  (isShown) => {
    if (isShown) {
      vendorId.value = props.vendors[0]?.id || "";
      requisitionId.value = "";
      currency.value = "USD";
      deliveryDate.value = "";
      deliveryAddress.value = "";
      notes.value = "";
      lines.value = [{ description: "", quantity: 1, unit: "each", unit_price: 0 }];
    }
  }
);

function onSubmit() {
  if (!vendorId.value || lines.value.length === 0) return;
  emit("submit", {
    vendor_id: vendorId.value,
    requisition_id: requisitionId.value || null,
    currency: currency.value,
    expected_delivery_date: deliveryDate.value || null,
    delivery_address: deliveryAddress.value.trim() || undefined,
    notes: notes.value.trim() || undefined,
    items: lines.value.map((l) => ({
      description: l.description.trim(),
      quantity: Number(l.quantity),
      unit: l.unit.trim(),
      unit_price: Number(l.unit_price),
    })),
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Issue Purchase Order"
    max-width="700px"
    @close="emit('close')"
  >
    <form id="create-po-form" @submit.prevent="onSubmit">
      <div class="form-row">
        <div class="form-group flex-2">
          <label class="form-label">Supplier / Vendor</label>
          <select v-model="vendorId" required class="form-select">
            <option value="" disabled>Select supplier</option>
            <option v-for="v in vendors" :key="v.id" :value="v.id">
              {{ v.name }} ({{ v.default_currency }})
            </option>
          </select>
        </div>
        <div class="form-group flex-1">
          <label class="form-label">Against Requisition (Optional)</label>
          <select v-model="requisitionId" class="form-select">
            <option value="">None (Direct Order)</option>
            <option
              v-for="r in requisitions.filter((r) => r.authorization_status === 'approved')"
              :key="r.id"
              :value="r.id"
            >
              {{ r.requisition_number }} - {{ r.title }}
            </option>
          </select>
        </div>
      </div>

      <div class="lines-section">
        <div class="lines-header">
          <h4>Contracted Line Items</h4>
          <button type="button" class="btn btn-secondary btn-xs" @click="addLine">
            + Add Item
          </button>
        </div>

        <div v-for="(line, idx) in lines" :key="idx" class="line-row">
          <input
            v-model="line.description"
            type="text"
            required
            placeholder="Description"
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
            v-model.number="line.unit_price"
            type="number"
            min="0"
            step="0.01"
            required
            placeholder="Unit Price"
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

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Currency</label>
          <input v-model="currency" type="text" maxlength="3" class="form-input" />
        </div>
        <div class="form-group">
          <label class="form-label">Expected Delivery Date</label>
          <input v-model="deliveryDate" type="date" class="form-input" />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Delivery Address</label>
        <input
          v-model="deliveryAddress"
          type="text"
          placeholder="Warehouse / Branch Address"
          class="form-input"
        />
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
        form="create-po-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Save Draft Order
      </button>
    </template>
  </ModalDialog>
</template>

<style scoped>
.form-row {
  display: flex;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.flex-2 {
  flex: 2;
}

.flex-1 {
  flex: 1;
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
