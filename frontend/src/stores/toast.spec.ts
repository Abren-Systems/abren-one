import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useToastStore } from "./toast";

describe("useToastStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("initializes with empty toasts", () => {
    const store = useToastStore();
    expect(store.toasts).toEqual([]);
  });

  it("adds a toast with default info kind and duration", () => {
    const store = useToastStore();
    const id = store.add("Test message");

    expect(store.toasts.length).toBe(1);
    expect(store.toasts[0]).toEqual({
      id,
      kind: "info",
      message: "Test message",
      duration: 4000,
    });
  });

  it("auto-dismisses toast after duration expires", () => {
    const store = useToastStore();
    store.add("Dismiss me", "info", 2000);

    expect(store.toasts.length).toBe(1);
    vi.advanceTimersByTime(2000);
    expect(store.toasts.length).toBe(0);
  });

  it("manually dismisses toast by id", () => {
    const store = useToastStore();
    const id = store.success("Saved");
    expect(store.toasts.length).toBe(1);

    store.dismiss(id);
    expect(store.toasts.length).toBe(0);
  });

  it("provides helper methods for success, error, info, warning", () => {
    const store = useToastStore();

    store.success("Success msg");
    store.error("Error msg");
    store.info("Info msg");
    store.warning("Warning msg");

    expect(store.toasts.length).toBe(4);
    expect(store.toasts[0].kind).toBe("success");
    expect(store.toasts[1].kind).toBe("error");
    expect(store.toasts[2].kind).toBe("info");
    expect(store.toasts[3].kind).toBe("warning");
  });
});
