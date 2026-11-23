<script setup lang="ts">
import { ref, watch, onMounted } from "vue";

const props = withDefaults(
  defineProps<{
    show: boolean;
    title: string;
    maxWidth?: string;
  }>(),
  {
    maxWidth: "540px",
  }
);

const emit = defineEmits<{
  (e: "close"): void;
}>();

const dialogRef = ref<HTMLDialogElement | null>(null);

function syncDialogState() {
  const dialog = dialogRef.value;
  if (!dialog) return;

  if (props.show) {
    if (!dialog.open) {
      dialog.showModal();
    }
  } else {
    if (dialog.open) {
      dialog.close();
    }
  }
}

watch(() => props.show, syncDialogState);
onMounted(syncDialogState);

function onCancel(e: Event) {
  // Prevent browser default dialog close so Vue state stays in sync
  e.preventDefault();
  emit("close");
}

function onBackdropClick(e: MouseEvent) {
  // Clicks directly on the <dialog> element (outside the inner content box) hit the backdrop
  if (e.target === dialogRef.value) {
    emit("close");
  }
}
</script>

<template>
  <dialog
    ref="dialogRef"
    class="native-modal"
    aria-labelledby="modal-title"
    @cancel="onCancel"
    @click="onBackdropClick"
    :style="{ maxWidth }"
  >
    <div class="modal-inner">
      <header class="modal-header">
        <slot name="header">
          <h2 id="modal-title" class="modal-title">{{ title }}</h2>
          <button
            type="button"
            class="modal-close-btn"
            aria-label="Close dialog"
            @click="emit('close')"
          >
            ✕
          </button>
        </slot>
      </header>

      <div class="modal-body">
        <slot></slot>
      </div>

      <footer v-if="$slots.footer" class="modal-footer">
        <slot name="footer"></slot>
      </footer>
    </div>
  </dialog>
</template>

<style scoped>
.native-modal {
  border: none;
  border-radius: var(--radius-lg);
  padding: 0;
  box-shadow: var(--shadow-lg);
  background-color: var(--color-surface);
  color: var(--color-text);
  width: 90vw;
  margin: auto;
}

/* Modern overscroll containment per modern-web-guidance */
.native-modal:modal {
  overscroll-behavior: contain;
}

.native-modal::backdrop {
  background-color: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  overflow: hidden;
  overscroll-behavior: contain;
}

.modal-inner {
  display: flex;
  flex-direction: column;
  max-height: 85vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
}

.modal-close-btn {
  background: transparent;
  border: none;
  font-size: 1.125rem;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: color 0.15s, background-color 0.15s;
}

.modal-close-btn:hover {
  color: var(--color-text);
  background-color: #f1f5f9;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
  background-color: #f8fafc;
  border-bottom-left-radius: var(--radius-lg);
  border-bottom-right-radius: var(--radius-lg);
}
</style>
