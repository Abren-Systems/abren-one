import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import DonorsTab from "./tabs/DonorsTab.vue";
import type { Donor } from "@/types/fundraising";

const mockDonors: Donor[] = [
  {
    id: "donor-1",
    organization_id: "org-1",
    name: "Oxfam Foundation",
    donor_type: "foundation",
    status: "active",
    is_active: true,
    email: "contact@oxfam.org",
    phone: "+44 1234 567",
  },
  {
    id: "donor-2",
    organization_id: "org-1",
    name: "Jane Doe",
    donor_type: "individual",
    status: "active",
    is_active: true,
    email: "jane@example.com",
    phone: "+1 555 0101",
  },
];

describe("DonorsTab", () => {
  it("renders list of donors", () => {
    const wrapper = mount(DonorsTab, {
      props: {
        donors: mockDonors,
      },
    });

    expect(wrapper.text()).toContain("Oxfam Foundation");
    expect(wrapper.text()).toContain("Jane Doe");
    expect(wrapper.findAll("tbody tr").length).toBe(2);
  });

  it("filters donors by search query", async () => {
    const wrapper = mount(DonorsTab, {
      props: {
        donors: mockDonors,
      },
    });

    const searchInput = wrapper.find('input[type="search"]');
    await searchInput.setValue("Jane");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("Jane Doe");
    expect(wrapper.text()).not.toContain("Oxfam Foundation");
  });

  it("filters donors by type", async () => {
    const wrapper = mount(DonorsTab, {
      props: {
        donors: mockDonors,
      },
    });

    const select = wrapper.find("select.filter-select");
    await select.setValue("foundation");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("Oxfam Foundation");
  });

  it("emits openCreateDonor when Add Donor clicked", async () => {
    const wrapper = mount(DonorsTab, {
      props: {
        donors: mockDonors,
      },
    });

    const btn = wrapper.find("button.btn-primary");
    await btn.trigger("click");

    expect(wrapper.emitted("openCreateDonor")).toHaveLength(1);
  });
});
