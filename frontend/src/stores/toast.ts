import { defineStore } from "pinia";
import { ref } from "vue";

export type ToastKind = "success" | "error" | "info" | "warning";

export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
  duration: number; // ms, 0 = persistent
}

let _nextId = 1;

export const useToastStore = defineStore("toast", () => {
  const toasts = ref<Toast[]>([]);

  function add(message: string, kind: ToastKind = "info", duration = 4000): number {
    const id = _nextId++;
    toasts.value.push({ id, kind, message, duration });

    if (duration > 0) {
      setTimeout(() => dismiss(id), duration);
    }

    return id;
  }

  function dismiss(id: number) {
    const idx = toasts.value.findIndex((t) => t.id === id);
    if (idx !== -1) toasts.value.splice(idx, 1);
  }

  function success(message: string | null | undefined, duration = 4000) {
    if (!message) return -1;
    return add(message, "success", duration);
  }

  function error(message: string | null | undefined, duration = 6000) {
    if (!message) return -1;
    return add(message, "error", duration);
  }

  function info(message: string | null | undefined, duration = 4000) {
    if (!message) return -1;
    return add(message, "info", duration);
  }

  function warning(message: string | null | undefined, duration = 5000) {
    if (!message) return -1;
    return add(message, "warning", duration);
  }

  return { toasts, add, dismiss, success, error, info, warning };
});
