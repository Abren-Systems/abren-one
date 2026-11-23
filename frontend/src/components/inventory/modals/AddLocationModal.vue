<script setup lang="ts">
import { ref } from "vue";
import ModalDialog from "@/components/common/ModalDialog.vue";

const props = defineProps<{
  show: boolean;
  warehouseId: string;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "submit",
    data: {
      warehouseId: string;
      name: string;
      code: string;
    }
  ): void;
}>();

const name = ref("");
const code = ref("");

function onSubmit() {
  if (!name.value.trim() || !code.value.trim() || !props.warehouseId) return;
  emit("submit", {
    warehouseId: props.warehouseId,
    name: name.value.trim(),
    code: code.value.trim().toUpperCase(),
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Add Storage Location"
    max-width="480px"
    @close="emit('close')"
  >
    <form id="add-location-form" @submit.prevent="onSubmit">
      <div class="form-group">
        <label class="form-label">Location Name</label>
        <input
          v-model="name"
          type="text"
          required
          placeholder="e.g. Shelf A, Row 3"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Location Code</label>
        <input
          v-model="code"
          type="text"
          required
          placeholder="e.g. SH-A3"
          class="form-input font-mono"
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
        form="add-location-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Add Location
      </button>
    </template>
  </ModalDialog>
</template>

<style scoped>
.font-mono {
  font-family: monospace;
}
</style>
