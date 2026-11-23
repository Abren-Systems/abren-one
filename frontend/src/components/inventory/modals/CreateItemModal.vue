<script setup lang="ts">
import { ref } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";
import type { ItemCategory } from "@/types/inventory";

defineProps<{
  show: boolean;
  categories: ItemCategory[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    data: {
      category_id: string;
      item_code: string;
      name: string;
      description?: string;
      unit_of_measure: string;
      item_type: string;
      track_batches: boolean;
      track_expiry: boolean;
      reorder_threshold: string;
      default_unit_cost: string;
    }
  ): void;
}>();

const form = ref({
  category_id: "",
  item_code: "",
  name: "",
  description: "",
  unit_of_measure: "each",
  item_type: "consumable",
  track_batches: false,
  track_expiry: false,
  reorder_threshold: "0.00",
  default_unit_cost: "0.00",
});

function onSubmit() {
  if (!form.value.name.trim() || !form.value.item_code.trim()) return;
  emit("submit", {
    ...form.value,
    reorder_threshold: form.value.reorder_threshold || "0.00",
    default_unit_cost: form.value.default_unit_cost || "0.00",
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Create Catalog Item"
    max-width="640px"
    @close="emit('close')"
  >
    <form id="create-item-form" @submit.prevent="onSubmit">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Category</label>
          <select v-model="form.category_id" required class="form-select">
            <option value="" disabled>Select category</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }})
            </option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Item Code</label>
          <input
            v-model="form.item_code"
            type="text"
            required
            placeholder="e.g. MED-KIT-01"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Item Name</label>
        <input
          v-model="form.name"
          type="text"
          required
          placeholder="e.g. Emergency First Aid Kit"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Description</label>
        <textarea
          v-model="form.description"
          rows="2"
          placeholder="Optional specifications..."
          class="form-textarea"
        ></textarea>
      </div>

      <div class="form-row three-col">
        <div class="form-group">
          <label class="form-label">Unit of Measure</label>
          <input
            v-model="form.unit_of_measure"
            type="text"
            required
            placeholder="each, kg, box"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Item Type</label>
          <select v-model="form.item_type" class="form-select">
            <option value="consumable">Consumable</option>
            <option value="durable_asset">Durable Asset</option>
            <option value="relief_good">Relief Good</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Reorder Level</label>
          <input
            v-model="form.reorder_threshold"
            type="number"
            step="0.01"
            min="0"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Default Unit Cost (USD)</label>
          <input
            v-model="form.default_unit_cost"
            type="number"
            step="0.01"
            min="0"
            class="form-input"
          />
        </div>
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input v-model="form.track_batches" type="checkbox" />
            <span>Track Batches / Lots</span>
          </label>
          <label class="checkbox-label">
            <input v-model="form.track_expiry" type="checkbox" />
            <span>Track Expiration Dates</span>
          </label>
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
        form="create-item-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Create Item
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

.three-col {
  grid-template-columns: 1fr 1fr 1fr;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: center;
  padding-top: 1rem;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text);
  cursor: pointer;
}
</style>
