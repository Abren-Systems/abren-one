import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import TrialBalanceTab from "./tabs/TrialBalanceTab.vue";
import type { TrialBalance } from "@/types/finance";

const mockBalancedTB: TrialBalance = {
  currency: "USD",
  total_debits: "15000.00",
  total_credits: "15000.00",
  is_balanced: true,
  items: [
    {
      account_id: "acc-1",
      code: "1010",
      name: "Cash and Bank",
      account_type: "asset",
      normal_balance: "debit",
      total_debit: "10000.00",
      total_credit: "0.00",
      balance_debit: "10000.00",
      balance_credit: "0.00",
    },
    {
      account_id: "acc-2",
      code: "1310",
      name: "Relief Inventory",
      account_type: "asset",
      normal_balance: "debit",
      total_debit: "5000.00",
      total_credit: "0.00",
      balance_debit: "5000.00",
      balance_credit: "0.00",
    },
    {
      account_id: "acc-3",
      code: "3010",
      name: "General Fund Equity",
      account_type: "equity",
      normal_balance: "credit",
      total_debit: "0.00",
      total_credit: "15000.00",
      balance_debit: "0.00",
      balance_credit: "15000.00",
    },
  ],
};

const mockUnbalancedTB: TrialBalance = {
  ...mockBalancedTB,
  total_credits: "14000.00",
  is_balanced: false,
};

describe("TrialBalanceTab", () => {
  it("renders empty state when trialBalance is null", () => {
    const wrapper = mount(TrialBalanceTab, {
      props: {
        trialBalance: null,
      },
    });

    expect(wrapper.text()).toContain("No Trial Balance Data");
  });

  it("renders balanced trial balance table and status badge", () => {
    const wrapper = mount(TrialBalanceTab, {
      props: {
        trialBalance: mockBalancedTB,
      },
    });

    expect(wrapper.text()).toContain("Authoritative Trial Balance");
    expect(wrapper.text()).toContain("LEDGER BALANCED");
    expect(wrapper.findAll("tbody tr").length).toBe(3);
    expect(wrapper.text()).toContain("15000.00");
  });

  it("renders unbalanced warning status badge when not balanced", () => {
    const wrapper = mount(TrialBalanceTab, {
      props: {
        trialBalance: mockUnbalancedTB,
      },
    });

    expect(wrapper.text()).toContain("UNBALANCED");
  });
});
