import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import DashboardView from "./DashboardView.vue";
import { useTenantStore } from "@/stores/tenant";
import { programsApi } from "@/api/modules/programs";
import { beneficiariesApi } from "@/api/modules/beneficiaries";
import { fundraisingApi } from "@/api/modules/fundraising";
import { procurementApi } from "@/api/modules/procurement";
import { inventoryApi } from "@/api/modules/inventory";

describe("DashboardView.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.restoreAllMocks();
  });

  it("shows empty banner when no organization is selected", () => {
    const wrapper = mount(DashboardView, {
      global: {
        stubs: ["router-link"],
      },
    });

    expect(wrapper.text()).toContain("No Organization Selected");
  });

  it("loads and displays operational metrics when tenant is selected", async () => {
    const tenantStore = useTenantStore();
    tenantStore.selectOrganization("org-test");

    vi.spyOn(programsApi, "getPrograms").mockResolvedValue([{ id: "p1" } as any]);
    vi.spyOn(beneficiariesApi, "getBeneficiaries").mockResolvedValue([
      { id: "b1" } as any,
      { id: "b2" } as any,
    ]);
    vi.spyOn(fundraisingApi, "getDonors").mockResolvedValue([{ id: "d1" } as any]);
    vi.spyOn(fundraisingApi, "getGrants").mockResolvedValue([{ id: "g1" } as any]);
    vi.spyOn(procurementApi, "getRequisitions").mockResolvedValue([
      { id: "r1" } as any,
      { id: "r2" } as any,
      { id: "r3" } as any,
    ]);
    vi.spyOn(inventoryApi, "getItems").mockResolvedValue([
      { id: "i1" } as any,
      { id: "i2" } as any,
    ]);

    const wrapper = mount(DashboardView, {
      global: {
        stubs: ["router-link"],
      },
    });

    // Wait for promises to settle
    await new Promise((r) => setTimeout(r, 10));

    expect(wrapper.text()).toContain("Operations Overview");
    expect(wrapper.text()).toContain("Active Programs");
    expect(wrapper.text()).toContain("Tracked Inventory Items");
    expect(wrapper.text()).toContain("Procurement Requisitions");

    const metricVals = wrapper.findAll(".metric-val");
    expect(metricVals.length).toBe(6);
    expect(metricVals[0].text()).toBe("1"); // Programs
    expect(metricVals[1].text()).toBe("2"); // Beneficiaries
    expect(metricVals[2].text()).toBe("1"); // Donors
    expect(metricVals[3].text()).toBe("1"); // Grants
    expect(metricVals[4].text()).toBe("3"); // Requisitions
    expect(metricVals[5].text()).toBe("2"); // Items
  });
});
