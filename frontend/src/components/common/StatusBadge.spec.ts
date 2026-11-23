import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import StatusBadge from "./StatusBadge.vue";

describe("StatusBadge", () => {
  it("renders capitalized formatted label", () => {
    const wrapper = mount(StatusBadge, {
      props: { status: "in_progress" },
    });
    expect(wrapper.text()).toBe("In Progress");
  });

  it("applies badge-success class for positive statuses", () => {
    const wrapper = mount(StatusBadge, {
      props: { status: "active" },
    });
    expect(wrapper.classes()).toContain("badge-success");
  });

  it("applies badge-warning class for draft/pending statuses", () => {
    const wrapper = mount(StatusBadge, {
      props: { status: "draft" },
    });
    expect(wrapper.classes()).toContain("badge-warning");
  });

  it("applies badge-danger class for rejected/cancelled statuses", () => {
    const wrapper = mount(StatusBadge, {
      props: { status: "rejected" },
    });
    expect(wrapper.classes()).toContain("badge-danger");
  });

  it("applies badge-neutral class for closed/inactive statuses", () => {
    const wrapper = mount(StatusBadge, {
      props: { status: "closed" },
    });
    expect(wrapper.classes()).toContain("badge-neutral");
  });
});
