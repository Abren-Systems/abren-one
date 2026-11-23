import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import BranchesTab from "./tabs/BranchesTab.vue";

const mockBranches = [
  {
    id: "branch-1",
    organization_id: "org-1",
    name: "Headquarters",
    code: "HQ",
    is_headquarters: true,
    is_active: true,
  },
  {
    id: "branch-2",
    organization_id: "org-1",
    name: "Field Office North",
    code: "FO-N",
    is_headquarters: false,
    is_active: true,
  },
];

describe("BranchesTab.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("renders all branches in a table", () => {
    const wrapper = mount(BranchesTab, {
      props: { branches: mockBranches },
    });

    const rows = wrapper.findAll("tbody tr");
    expect(rows.length).toBe(2);
    expect(rows[0].text()).toContain("Headquarters");
    expect(rows[0].text()).toContain("HQ");
    expect(rows[1].text()).toContain("Field Office North");
  });

  it("filters branches by search query", async () => {
    const wrapper = mount(BranchesTab, {
      props: { branches: mockBranches },
    });

    const searchInput = wrapper.find("input[type='search']");
    await searchInput.setValue("north");

    const rows = wrapper.findAll("tbody tr");
    expect(rows.length).toBe(1);
    expect(rows[0].text()).toContain("Field Office North");
  });

  it("shows empty state when no branches exist", () => {
    const wrapper = mount(BranchesTab, {
      props: { branches: [] },
    });

    expect(wrapper.find("tbody").exists()).toBe(false);
    expect(wrapper.text()).toContain("No Branches Found");
  });

  it("emits openCreateBranch when button clicked", async () => {
    const wrapper = mount(BranchesTab, {
      props: { branches: mockBranches },
    });

    await wrapper.find("button.btn-primary").trigger("click");
    expect(wrapper.emitted("openCreateBranch")).toBeTruthy();
  });
});
