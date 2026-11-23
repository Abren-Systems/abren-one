import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import AccountsTab from "./tabs/AccountsTab.vue";
import type { Account } from "@/types/finance";

const mockAccounts: Account[] = [
  {
    id: "acc-1",
    code: "1010",
    name: "Cash and Bank",
    account_type: "asset",
    currency: "USD",
    is_active: true,
  },
  {
    id: "acc-2",
    code: "2010",
    name: "Accounts Payable",
    account_type: "liability",
    currency: "USD",
    is_active: true,
  },
  {
    id: "acc-3",
    code: "5010",
    name: "Emergency Relief Supplies",
    account_type: "expense",
    currency: "USD",
    is_active: true,
  },
];

describe("AccountsTab", () => {
  it("renders accounts table with all accounts", () => {
    const wrapper = mount(AccountsTab, {
      props: {
        accounts: mockAccounts,
      },
    });

    expect(wrapper.text()).toContain("1010");
    expect(wrapper.text()).toContain("Cash and Bank");
    expect(wrapper.text()).toContain("2010");
    expect(wrapper.text()).toContain("Accounts Payable");
    expect(wrapper.findAll("tbody tr").length).toBe(3);
  });

  it("filters accounts by search query", async () => {
    const wrapper = mount(AccountsTab, {
      props: {
        accounts: mockAccounts,
      },
    });

    const searchInput = wrapper.find('input[type="search"]');
    await searchInput.setValue("Relief");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("Emergency Relief Supplies");
    expect(wrapper.text()).not.toContain("Cash and Bank");
  });

  it("filters accounts by account type", async () => {
    const wrapper = mount(AccountsTab, {
      props: {
        accounts: mockAccounts,
      },
    });

    const select = wrapper.find("select.filter-select");
    await select.setValue("liability");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("Accounts Payable");
    expect(wrapper.text()).not.toContain("Cash and Bank");
  });

  it("shows empty state when no accounts match filters", async () => {
    const wrapper = mount(AccountsTab, {
      props: {
        accounts: mockAccounts,
      },
    });

    const searchInput = wrapper.find('input[type="search"]');
    await searchInput.setValue("nonexistent code or keyword");

    expect(wrapper.findAll("tbody tr").length).toBe(0);
    expect(wrapper.text()).toContain("No Accounts Found");
  });

  it("emits openCreateAccount event when button clicked", async () => {
    const wrapper = mount(AccountsTab, {
      props: {
        accounts: mockAccounts,
      },
    });

    const btn = wrapper.find("button.btn-primary");
    await btn.trigger("click");

    expect(wrapper.emitted("openCreateAccount")).toHaveLength(1);
  });
});
