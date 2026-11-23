<script setup lang="ts">
import { ref } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  show: boolean;
  itemId: string;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    data: {
      itemId: string;
      batch_number: string;
      manufacture_date?: string;
      expiry_date?: string;
    }
  ): void;
}>();

const batchNumber = ref("");
const manufactureDate = ref("");
const expiryDate = ref("");

function onSubmit() {
  if (!batchNumber.value.trim() || !props.itemId) return;
  emit("submit", {
    itemId: props.itemId,
    batch_number: batchNumber.value.trim(),
    manufacture_date: manufactureDate.value || undefined,
    expiry_date: expiryDate.value || undefined,
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Register Item Batch / Lot"
    max-width="480px"
    @close="emit('close')"
  >
    <form id="add-batch-form" @submit.prevent="onSubmit">
      <div class="form-group">
        <label class="form-label">Batch / Lot Number</label>
        <input
          v-model="batchNumber"
          type="text"
          required
          placeholder="e.g. LOT-2026-X"
          class="form-input font-mono"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Manufacture Date</label>
          <input
            v-model="manufactureDate"
            type="date"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Expiry Date</label>
          <input
            v-model="expiryDate"
            type="date"
            class="form-input"
          />
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
        form="add-batch-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Register Batch
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

.font-mono {
  font-family: monospace;
}
</style>
