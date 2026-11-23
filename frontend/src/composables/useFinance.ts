import { ref, watch, onMounted, getCurrentInstance } from "vue";
import { financeApi } from "@/api/modules/finance";
import { useTenantStore } from "@/stores/tenant";
import type {
  Account,
  CreateAccountPayload,
  CreateJournalEntryPayload,
  JournalEntry,
  TrialBalance,
} from "@/types/finance";

export function useFinance() {
  const tenantStore = useTenantStore();

  const accounts = ref<Account[]>([]);
  const journalEntries = ref<JournalEntry[]>([]);
  const trialBalance = ref<TrialBalance | null>(null);
  const selectedEntry = ref<JournalEntry | null>(null);

  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadData() {
    if (!tenantStore.currentOrganizationId) return;
    isLoading.value = true;
    errorMessage.value = null;

    try {
      const [accsRes, entriesRes, tbRes] = await Promise.all([
        financeApi.getAccounts().catch(() => []),
        financeApi.getJournalEntries().catch(() => []),
        financeApi.getTrialBalance().catch(() => null),
      ]);

      accounts.value = accsRes;
      journalEntries.value = entriesRes;
      trialBalance.value = tbRes;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load financial records.";
    } finally {
      isLoading.value = false;
    }
  }

  async function createAccount(data: CreateAccountPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await financeApi.createAccount(data);
      successMessage.value = `Account ${data.code} created successfully.`;
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to create account.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createJournalEntry(data: CreateJournalEntryPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await financeApi.createJournalEntry(data);
      successMessage.value = "Journal entry recorded successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to record journal entry.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function postJournalEntry(id: string) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      await financeApi.postJournalEntry(id);
      successMessage.value = "Journal entry posted to general ledger.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to post journal entry.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function reverseJournalEntry(id: string, reason: string) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await financeApi.reverseJournalEntry(id, reason);
      successMessage.value = "Journal entry reversed with offsetting entry.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to reverse journal entry.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearMessages() {
    errorMessage.value = null;
    successMessage.value = null;
  }

  watch(
    () => tenantStore.currentOrganizationId,
    () => {
      loadData();
    }
  );

  if (getCurrentInstance()) {
    onMounted(() => {
      loadData();
    });
  }

  return {
    // State
    accounts,
    journalEntries,
    trialBalance,
    selectedEntry,
    isLoading,
    errorMessage,
    successMessage,

    // Actions
    loadData,
    createAccount,
    createJournalEntry,
    postJournalEntry,
    reverseJournalEntry,
    clearMessages,
  };
}
