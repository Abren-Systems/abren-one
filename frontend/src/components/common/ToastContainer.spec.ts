import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import ToastContainer from "./ToastContainer.vue";
import { useToastStore } from "@/stores/toast";

describe("ToastContainer.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("renders toasts from store into document body via teleport", async () => {
    const store = useToastStore();
    store.success("Operation successful!");

    const wrapper = mount(ToastContainer, {
      attachTo: document.body,
    });

    const toastElement = document.querySelector(".toast--success");
    expect(toastElement).not.toBeNull();
    expect(toastElement?.textContent).toContain("Operation successful!");

    wrapper.unmount();
  });

  it("dismisses toast when close button is clicked", async () => {
    const store = useToastStore();
    const id = store.error("An error occurred");

    const wrapper = mount(ToastContainer, {
      attachTo: document.body,
    });

    const closeBtn = document.querySelector(".toast__close") as HTMLButtonElement;
    expect(closeBtn).not.toBeNull();
    closeBtn.click();

    expect(store.toasts.find((t) => t.id === id)).toBeUndefined();
    wrapper.unmount();
  });
});
