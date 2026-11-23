<script setup lang="ts">
import { ref } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";

defineProps<{
  show: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    data: {
      name: string;
      code: string;
      warehouse_type: string;
      address?: string;
    }
  ): void;
}>();

const form = ref({
  name: "",
  code: "",
  warehouse_type: "regional_depot",
  address: "",
});

function onSubmit() {
  if (!form.value.name.trim() || !form.value.code.trim()) return;
  emit("submit", {
    name: form.value.name.trim(),
    code: form.value.code.trim().toUpperCase(),
    warehouse_type: form.value.warehouse_type,
    address: form.value.address.trim(),
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Create Storage Facility / Warehouse"
    max-width="500px"
    @close="emit('close')"
  >
    <form id="create-warehouse-form" @submit.prevent="onSubmit">
      <div class="form-group">
        <label class="form-label">Warehouse Name</label>
        <input
          v-model="form.name"
          type="text"
          required
          placeholder="e.g. Central Supply Hub"
          class="form-input"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Code</label>
          <input
            v-model="form.code"
            type="text"
            required
            placeholder="e.g. WH-CENTRAL"
            class="form-input font-mono"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="form.warehouse_type" class="form-select">
            <option value="central_warehouse">Central Warehouse</option>
            <option value="regional_depot">Regional Depot</option>
            <option value="field_post">Field Post</option>
            <option value="transit_hub">Transit Hub</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Address / Location</label>
        <textarea
          v-model="form.address"
          rows="2"
          placeholder="Physical address or GPS coordinates..."
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
        form="create-warehouse-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Create Warehouse
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
