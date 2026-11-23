<script setup lang="ts">
import { useToastStore } from "@/stores/toast";
import type { Toast } from "@/stores/toast";

const store = useToastStore();

const icons: Record<Toast["kind"], string> = {
  success: "✓",
  error: "✕",
  warning: "⚠",
  info: "ℹ",
};
</script>

<template>
  <Teleport to="body">
    <div class="toast-container" role="region" aria-label="Notifications" aria-live="polite">
      <Transition
        v-for="toast in store.toasts"
        :key="toast.id"
        name="toast"
        appear
      >
        <div
          :class="['toast', `toast--${toast.kind}`]"
          role="alert"
        >
          <span class="toast__icon" aria-hidden="true">{{ icons[toast.kind] }}</span>
          <span class="toast__message">{{ toast.message }}</span>
          <button
            class="toast__close"
            type="button"
            :aria-label="`Dismiss: ${toast.message}`"
            @click="store.dismiss(toast.id)"
          >
            ×
          </button>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 9000;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  max-width: 400px;
  width: calc(100vw - 2.5rem);
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.08);
  font-size: 0.875rem;
  font-weight: 500;
  pointer-events: auto;
  line-height: 1.4;
  min-height: 48px;
}

.toast--success {
  background-color: #f0fdf4;
  border: 1px solid #86efac;
  color: #14532d;
}

.toast--error {
  background-color: #fef2f2;
  border: 1px solid #fca5a5;
  color: #7f1d1d;
}

.toast--warning {
  background-color: #fffbeb;
  border: 1px solid #fcd34d;
  color: #78350f;
}

.toast--info {
  background-color: #eff6ff;
  border: 1px solid #93c5fd;
  color: #1e3a8a;
}

.toast__icon {
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 0.05rem;
}

.toast__message {
  flex: 1;
}

.toast__close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  padding: 0;
  color: inherit;
  opacity: 0.5;
  flex-shrink: 0;
  margin-top: -0.1rem;
  transition: opacity 0.1s;
}

.toast__close:hover {
  opacity: 1;
}

/* Transitions */
.toast-enter-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-leave-active {
  transition: all 0.2s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(1.5rem) scale(0.96);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(1.5rem);
}
</style>
