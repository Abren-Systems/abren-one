import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import BeneficiariesTab from "./tabs/BeneficiariesTab.vue";
import type { Beneficiary } from "@/types/beneficiary";

const mockBens: Beneficiary[] = [
  {
    id: "ben-1",
    organization_id: "org-1",
    beneficiary_type: "individual",
    identification_number: "ID-100",
    display_name: "Amina Yusuf",
    first_name: "Amina",
    last_name: "Yusuf",
    household_name: "",
    status: "active",
    vulnerability_level: "high",
    contact_phone: "+251 91 000 0000",
    contact_address: "Camp A",
    is_active: true,
  },
  {
    id: "ben-2",
    organization_id: "org-1",
    beneficiary_type: "household",
    identification_number: "HH-200",
    display_name: "Mohamed Family",
    first_name: "",
    last_name: "",
    household_name: "Mohamed Family",
    status: "active",
    vulnerability_level: "critical",
    contact_phone: "+251 91 111 1111",
    contact_address: "Camp B",
    is_active: true,
  },
];

describe("BeneficiariesTab", () => {
  it("renders list of beneficiaries", () => {
    const wrapper = mount(BeneficiariesTab, {
      props: {
        beneficiaries: mockBens,
      },
    });

    expect(wrapper.text()).toContain("Amina Yusuf");
    expect(wrapper.text()).toContain("Mohamed Family");
    expect(wrapper.findAll("tbody tr").length).toBe(2);
  });

  it("filters beneficiaries by search query", async () => {
    const wrapper = mount(BeneficiariesTab, {
      props: {
        beneficiaries: mockBens,
      },
    });

    const searchInput = wrapper.find('input[type="search"]');
    await searchInput.setValue("Mohamed");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("Mohamed Family");
    expect(wrapper.text()).not.toContain("Amina Yusuf");
  });

  it("filters beneficiaries by vulnerability level", async () => {
    const wrapper = mount(BeneficiariesTab, {
      props: {
        beneficiaries: mockBens,
      },
    });

    const select = wrapper.find("select.filter-select");
    await select.setValue("critical");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("Mohamed Family");
  });

  it("emits openRegister when Register Beneficiary button is clicked", async () => {
    const wrapper = mount(BeneficiariesTab, {
      props: {
        beneficiaries: mockBens,
      },
    });

    const btn = wrapper.find("button.btn-primary");
    await btn.trigger("click");

    expect(wrapper.emitted("openRegister")).toHaveLength(1);
  });
});
