import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import EmptyState from "./EmptyState.vue";

describe("EmptyState", () => {
  it("renders title and message correctly", () => {
    const wrapper = mount(EmptyState, {
      props: {
        title: "No Items Registered",
        message: "Get started by adding your first inventory item.",
      },
    });
    expect(wrapper.find(".empty-state-title").text()).toBe("No Items Registered");
    expect(wrapper.find(".empty-state-message").text()).toBe(
      "Get started by adding your first inventory item."
    );
  });

  it("renders action slot content when provided", () => {
    const wrapper = mount(EmptyState, {
      props: { title: "Empty List" },
      slots: {
        action: '<button class="test-btn">Add New</button>',
      },
    });
    const btn = wrapper.find(".test-btn");
    expect(btn.exists()).toBe(true);
    expect(btn.text()).toBe("Add New");
  });
});
