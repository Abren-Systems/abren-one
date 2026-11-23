import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import SkeletonLoader from "./SkeletonLoader.vue";

describe("SkeletonLoader.vue", () => {
  it("renders default 4 skeleton rows", () => {
    const wrapper = mount(SkeletonLoader);
    const bars = wrapper.findAll(".skeleton__bar");
    expect(bars.length).toBe(4);
    expect(wrapper.find(".skeleton__bar--header").exists()).toBe(false);
  });

  it("renders custom row count and header bar when requested", () => {
    const wrapper = mount(SkeletonLoader, {
      props: {
        rows: 6,
        header: true,
        headerWidth: "60%",
      },
    });

    expect(wrapper.find(".skeleton__bar--header").exists()).toBe(true);
    const regularBars = wrapper.findAll(".skeleton__bar:not(.skeleton__bar--header)");
    expect(regularBars.length).toBe(6);
  });
});
