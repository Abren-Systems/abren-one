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
      name: string;
      code: string;
      description?: string;
      parent_id?: string | null;
    }
  ): void;
}>();

const form = ref({
  name: "",
  code: "",
  description: "",
  parent_id: "" as string | null,
});

function onSubmit() {
  if (!form.value.name.trim() || !form.value.code.trim()) return;
  emit("submit", {
    name: form.value.name.trim(),
    code: form.value.code.trim(),
    description: form.value.description.trim(),
    parent_id: form.value.parent_id || null,
  });
}
</script>

<template>
  <ModalDialog
    :show="show"
    title="Create Item Category"
    max-width="480px"
    @close="emit('close')"
  >
    <form id="create-category-form" @submit.prevent="onSubmit">
      <div class="form-group">
        <label class="form-label">Category Name</label>
        <input
          v-model="form.name"
          type="text"
          required
          placeholder="e.g. Water & Sanitation (WASH)"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Category Code</label>
        <input
          v-model="form.code"
          type="text"
          required
          placeholder="e.g. WASH"
          class="form-input font-mono"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Parent Category (Optional)</label>
        <select v-model="form.parent_id" class="form-select">
          <option :value="null">None (Top-Level Category)</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">Description</label>
        <textarea
          v-model="form.description"
          rows="2"
          placeholder="Optional category description..."
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
        form="create-category-form"
        class="btn btn-primary"
        :disabled="isLoading"
      >
        Create Category
      </button>
    </template>
  </ModalDialog>
</template>

<style scoped>
.font-mono {
  font-family: monospace;
}
</style>
