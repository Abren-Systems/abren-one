import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useFinance } from "./useFinance";
import { financeApi } from "@/api/modules/finance";
import { useTenantStore } from "@/stores/tenant";
import type { TrialBalance } from "@/types/finance";

const mockEmptyTB: TrialBalance = {
  currency: "USD",
  items: [],
  total_debits: "0.00",
  total_credits: "0.00",
  is_balanced: true,
};

describe("useFinance composable", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const tenant = useTenantStore();
    tenant.selectOrganization("org-finance-test-1");
    vi.restoreAllMocks();
  });

  it("loads accounts, journal entries, and trial balance successfully", async () => {
    vi.spyOn(financeApi, "getAccounts").mockResolvedValue([
      {
        id: "acc-1",
        code: "1010",
        name: "Cash and Cash Equivalents",
        account_type: "asset",
        currency: "USD",
        is_active: true,
      },
    ]);
    vi.spyOn(financeApi, "getJournalEntries").mockResolvedValue([
      {
        id: "entry-1",
        entry_number: "JE-2026-0001",
        entry_date: "2026-01-01",
        memo: "Initial Capital Contribution",
        currency: "USD",
        status: "draft",
        total_amount: "1000.00",
        reversal_of_id: null,
      },
    ]);
    vi.spyOn(financeApi, "getTrialBalance").mockResolvedValue(mockEmptyTB);

    const finance = useFinance();
    await finance.loadData();

    expect(finance.accounts.value.length).toBe(1);
    expect(finance.accounts.value[0].code).toBe("1010");
    expect(finance.journalEntries.value.length).toBe(1);
    expect(finance.journalEntries.value[0].entry_number).toBe("JE-2026-0001");
    expect(finance.trialBalance.value?.is_balanced).toBe(true);
    expect(finance.isLoading.value).toBe(false);
    expect(finance.errorMessage.value).toBeNull();
  });

  it("creates account and refreshes state", async () => {
    const createSpy = vi.spyOn(financeApi, "createAccount").mockResolvedValue({ account_id: "acc-new" });
    vi.spyOn(financeApi, "getAccounts").mockResolvedValue([]);
    vi.spyOn(financeApi, "getJournalEntries").mockResolvedValue([]);
    vi.spyOn(financeApi, "getTrialBalance").mockResolvedValue(mockEmptyTB);

    const finance = useFinance();
    await finance.createAccount({
      code: "1200",
      name: "Accounts Receivable",
      account_type: "asset",
      currency: "USD",
    });

    expect(createSpy).toHaveBeenCalledWith({
      code: "1200",
      name: "Accounts Receivable",
      account_type: "asset",
      currency: "USD",
    });
    expect(finance.successMessage.value).toBe("Account 1200 created successfully.");
  });

  it("creates journal entry and refreshes state", async () => {
    const createSpy = vi.spyOn(financeApi, "createJournalEntry").mockResolvedValue({ entry_id: "entry-new" });
    vi.spyOn(financeApi, "getAccounts").mockResolvedValue([]);
    vi.spyOn(financeApi, "getJournalEntries").mockResolvedValue([]);
    vi.spyOn(financeApi, "getTrialBalance").mockResolvedValue(mockEmptyTB);

    const finance = useFinance();
    await finance.createJournalEntry({
      entry_date: "2026-01-02",
      memo: "Office Supplies",
      lines: [
        { account_id: "acc-1", debit: 100, credit: 0, memo: "Supplies" },
        { account_id: "acc-2", debit: 0, credit: 100, memo: "Cash paid" },
      ],
    });

    expect(createSpy).toHaveBeenCalled();
    expect(finance.successMessage.value).toBe("Journal entry recorded successfully.");
  });

  it("posts journal entry to general ledger", async () => {
    const postSpy = vi.spyOn(financeApi, "postJournalEntry").mockResolvedValue(undefined);
    vi.spyOn(financeApi, "getAccounts").mockResolvedValue([]);
    vi.spyOn(financeApi, "getJournalEntries").mockResolvedValue([]);
    vi.spyOn(financeApi, "getTrialBalance").mockResolvedValue(mockEmptyTB);

    const finance = useFinance();
    await finance.postJournalEntry("entry-123");

    expect(postSpy).toHaveBeenCalledWith("entry-123");
    expect(finance.successMessage.value).toBe("Journal entry posted to general ledger.");
  });

  it("reverses journal entry and sets success message", async () => {
    const reverseSpy = vi.spyOn(financeApi, "reverseJournalEntry").mockResolvedValue({ reversal_entry_id: "rev-999" });
    vi.spyOn(financeApi, "getAccounts").mockResolvedValue([]);
    vi.spyOn(financeApi, "getJournalEntries").mockResolvedValue([]);
    vi.spyOn(financeApi, "getTrialBalance").mockResolvedValue(mockEmptyTB);

    const finance = useFinance();
    await finance.reverseJournalEntry("entry-123", "Duplicate entry error");

    expect(reverseSpy).toHaveBeenCalledWith("entry-123", "Duplicate entry error");
    expect(finance.successMessage.value).toBe("Journal entry reversed with offsetting entry.");
  });

  it("clears messages on call", () => {
    const finance = useFinance();
    finance.errorMessage.value = "An error occurred";
    finance.successMessage.value = "Success!";
    finance.clearMessages();

    expect(finance.errorMessage.value).toBeNull();
    expect(finance.successMessage.value).toBeNull();
  });
});
