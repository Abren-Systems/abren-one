import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import ProgramsTab from "./tabs/ProgramsTab.vue";

const mockPrograms = [
  {
    id: "prog-1",
    organization_id: "org-1",
    name: "Health & Nutrition Response",
    description: "Multi-year health program",
    start_date: "2026-01-01",
    end_date: "2026-12-31",
    is_active: true,
    status: "active",
  },
  {
    id: "prog-2",
    organization_id: "org-1",
    name: "Emergency Relief",
    description: "Rapid response program",
    start_date: null,
    end_date: null,
    is_active: true,
    status: "active",
  },
];

describe("ProgramsTab.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("renders all programs in a table", () => {
    const wrapper = mount(ProgramsTab, {
      props: { programs: mockPrograms },
    });

    const rows = wrapper.findAll("tbody tr");
    expect(rows.length).toBe(2);
    expect(rows[0].text()).toContain("Health & Nutrition Response");
    expect(rows[1].text()).toContain("Emergency Relief");
  });

  it("filters programs by search query", async () => {
    const wrapper = mount(ProgramsTab, {
      props: { programs: mockPrograms },
    });

    const searchInput = wrapper.find("input[type='search']");
    await searchInput.setValue("emergency");

    const rows = wrapper.findAll("tbody tr");
    expect(rows.length).toBe(1);
    expect(rows[0].text()).toContain("Emergency Relief");
  });

  it("shows empty state when no programs exist", () => {
    const wrapper = mount(ProgramsTab, {
      props: { programs: [] },
    });

    expect(wrapper.find("tbody").exists()).toBe(false);
    expect(wrapper.text()).toContain("No Programs Found");
  });

  it("emits openCreateProgram when button clicked", async () => {
    const wrapper = mount(ProgramsTab, {
      props: { programs: mockPrograms },
    });

    await wrapper.find("button.btn-primary").trigger("click");
    expect(wrapper.emitted("openCreateProgram")).toBeTruthy();
  });
});
