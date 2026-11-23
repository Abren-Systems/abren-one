<script setup lang="ts">
import { ref, computed, watch } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";
import type { ItemSummary, WarehouseSummary } from "@/types/inventory";

export type MovementType =
  | "opening"
  | "donation"
  | "transfer"
  | "issue"
  | "adjust"
  | "write_off";

const props = defineProps<{
  show: boolean;
  type: MovementType;
  warehouses: WarehouseSummary[];
  items: ItemSummary[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "submit", payload: { endpoint: string; data: Record<string, unknown> }): void;
}>();

const modalTitle = computed(() => {
  switch (props.type) {
    case "opening":
      return "Record Opening Stock";
    case "donation":
      return "Record In-Kind Donation Receipt";
    case "transfer":
      return "Execute Inter-Warehouse Transfer";
    case "issue":
      return "Issue Supplies from Warehouse";
    case "adjust":
      return "Reconcile Physical Inventory Count";
    case "write_off":
      return "Record Stock Write-Off / Loss";
  }
});

// Common fields
const warehouseId = ref("");
const destWarehouseId = ref("");
const transactionDate = ref(new Date().toISOString().split("T")[0]);
const referenceDocument = ref("");
const notes = ref("");

// Type-specific fields
const donorName = ref("");
const recipientName = ref("");
const isProgramIssue = ref(true);
const justification = ref("");
const approvalReference = ref("");

// Lines
interface MovementLine {
  item_id: string;
  quantity: number;
  unit_cost: number;
  actual_quantity_counted: number;
  reason: string;
  batch_id: string;
}

const lines = ref<MovementLine[]>([
  {
    item_id: "",
    quantity: 1,
    unit_cost: 0,
    actual_quantity_counted: 0,
    reason: "",
    batch_id: "",
  },
]);

function addLine() {
  lines.value.push({
    item_id: "",
    quantity: 1,
    unit_cost: 0,
    actual_quantity_counted: 0,
    reason: "",
    batch_id: "",
  });
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
      warehouseId.value = props.warehouses[0]?.id || "";
      destWarehouseId.value = props.warehouses[1]?.id || "";
      transactionDate.value = new Date().toISOString().split("T")[0];
      referenceDocument.value = "";
      notes.value = "";
      donorName.value = "";
      recipientName.value = "";
      justification.value = "";
      approvalReference.value = "";
      lines.value = [
        {
          item_id: props.items[0]?.id || "",
          quantity: 1,
          unit_cost: 0,
          actual_quantity_counted: 0,
          reason: "",
          batch_id: "",
        },
      ];
    }
  }
);

function onSubmit() {
  switch (props.type) {
    case "opening":
      emit("submit", {
        endpoint: "receipt-opening",
        data: {
          warehouse_id: warehouseId.value,
          transaction_date: transactionDate.value,
          reference_document: referenceDocument.value,
          notes: notes.value,
          lines: lines.value.map((l) => ({
            item_id: l.item_id,
            quantity: l.quantity,
            unit_cost: l.unit_cost,
            batch_id: l.batch_id || null,
          })),
        },
      });
      break;

    case "donation":
      emit("submit", {
        endpoint: "receipt-donation",
        data: {
          warehouse_id: warehouseId.value,
          donor_name: donorName.value.trim(),
          transaction_date: transactionDate.value,
          reference_document: referenceDocument.value,
          notes: notes.value,
          lines: lines.value.map((l) => ({
            item_id: l.item_id,
            quantity: l.quantity,
            unit_cost: l.unit_cost,
            batch_id: l.batch_id || null,
          })),
        },
      });
      break;

    case "transfer":
      emit("submit", {
        endpoint: "transfer",
        data: {
          source_warehouse_id: warehouseId.value,
          destination_warehouse_id: destWarehouseId.value,
          transaction_date: transactionDate.value,
          reference_document: referenceDocument.value,
          notes: notes.value,
          lines: lines.value.map((l) => ({
            item_id: l.item_id,
            quantity: l.quantity,
            batch_id: l.batch_id || null,
          })),
        },
      });
      break;

    case "issue":
      emit("submit", {
        endpoint: "issue",
        data: {
          warehouse_id: warehouseId.value,
          transaction_date: transactionDate.value,
          is_program_issue: isProgramIssue.value,
          recipient_name: recipientName.value,
          reference_document: referenceDocument.value,
          notes: notes.value,
          lines: lines.value.map((l) => ({
            item_id: l.item_id,
            quantity: l.quantity,
            batch_id: l.batch_id || null,
          })),
        },
      });
      break;

    case "adjust":
      emit("submit", {
        endpoint: "adjust",
        data: {
          warehouse_id: warehouseId.value,
          transaction_date: transactionDate.value,
          justification: justification.value.trim(),
          reference_document: referenceDocument.value,
          lines: lines.value.map((l) => ({
            item_id: l.item_id,
            actual_quantity_counted: l.actual_quantity_counted,
            batch_id: l.batch_id || null,
            reason: l.reason,
          })),
        },
      });
      break;

    case "write_off":
      emit("submit", {
        endpoint: "write-off",
        data: {
          warehouse_id: warehouseId.value,
          transaction_date: transactionDate.value,
          approval_reference: approvalReference.value.trim(),
          justification: justification.value.trim(),
          lines: lines.value.map((l) => ({
            item_id: l.item_id,
            quantity: l.quantity,
            reason: l.reason,
            batch_id: l.batch_id || null,
          })),
        },
      });
      break;
  }
}
</script>

<template>
  <ModalDialog
    :show="show"
    :title="modalTitle"
    max-width="680px"
    @close="emit('close')"
  >
    <form id="movement-form" @submit.prevent="onSubmit">
      <!-- Warehouse selects -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">
            {{ type === "transfer" ? "Source Warehouse" : "Warehouse" }}
          </label>
          <select v-model="warehouseId" required class="form-select">
            <option value="" disabled>Select warehouse</option>
            <option v-for="w in warehouses" :key="w.id" :value="w.id">
              {{ w.name }} ({{ w.code }})
            </option>
          </select>
        </div>

        <div v-if="type === 'transfer'" class="form-group">
          <label class="form-label">Destination Warehouse</label>
          <select v-model="destWarehouseId" required class="form-select">
            <option value="" disabled>Select destination</option>
            <option v-for="w in warehouses" :key="w.id" :value="w.id">
              {{ w.name }} ({{ w.code }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Date</label>
          <input v-model="transactionDate" type="date" required class="form-input" />
        </div>
      </div>

      <!-- Specific header inputs -->
      <div v-if="type === 'donation'" class="form-group">
        <label class="form-label">Donor Name / Agency</label>
        <input
          v-model="donorName"
          type="text"
          required
          placeholder="e.g. UNICEF, USAID, Red Cross"
          class="form-input"
        />
      </div>

      <div v-if="type === 'issue'" class="form-row">
        <div class="form-group">
          <label class="form-label">Recipient Name / Community</label>
          <input
            v-model="recipientName"
            type="text"
            required
            placeholder="e.g. Ward 4 Clinic Staff"
            class="form-input"
          />
        </div>
        <div class="form-group checkbox-cell">
          <label class="checkbox-label">
            <input v-model="isProgramIssue" type="checkbox" />
            <span>Program Relief Activity</span>
          </label>
        </div>
      </div>

      <div v-if="type === 'adjust' || type === 'write_off'" class="form-row">
        <div v-if="type === 'write_off'" class="form-group">
          <label class="form-label">Approval Reference #</label>
          <input
            v-model="approvalReference"
            type="text"
            required
            placeholder="e.g. BOARD-APPROVAL-2026-09"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Justification / Reason</label>
          <input
            v-model="justification"
            type="text"
            required
            placeholder="Reason for discrepancy or write-off"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Reference Document / Waybill #</label>
        <input
          v-model="referenceDocument"
          type="text"
          placeholder="Optional tracking reference..."
          class="form-input"
        />
      </div>

      <!-- Lines Section -->
      <div class="lines-section">
        <div class="lines-header">
          <h4>Items & Quantities</h4>
          <button type="button" class="btn btn-secondary btn-xs" @click="addLine">
            + Add Line
          </button>
        </div>

        <div v-for="(line, idx) in lines" :key="idx" class="line-row">
          <select v-model="line.item_id" required class="form-select flex-2">
            <option value="" disabled>Select Item</option>
            <option v-for="item in items" :key="item.id" :value="item.id">
              {{ item.name }} ({{ item.item_code }})
            </option>
          </select>

          <input
            v-if="type === 'adjust'"
            v-model.number="line.actual_quantity_counted"
            type="number"
            step="0.01"
            min="0"
            required
            placeholder="Counted Qty"
            class="form-input flex-1"
          />
          <input
            v-else
            v-model.number="line.quantity"
            type="number"
            step="0.01"
            min="0.01"
            required
            placeholder="Quantity"
            class="form-input flex-1"
          />

          <input
            v-if="type === 'opening' || type === 'donation'"
            v-model.number="line.unit_cost"
            type="number"
            step="0.01"
            min="0"
            placeholder="Unit Cost ($)"
            class="form-input flex-1"
          />

          <input
            v-if="type === 'adjust' || type === 'write_off'"
            v-model="line.reason"
            type="text"
            placeholder="Discrepancy reason"
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
        form="movement-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Post to Ledger
      </button>
    </template>
  </ModalDialog>
</template>

<style scoped>
.form-row {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.form-row > * {
  flex: 1;
}

.checkbox-cell {
  padding-bottom: 0.5rem;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.lines-section {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-top: 1rem;
  background-color: #f8fafc;
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
