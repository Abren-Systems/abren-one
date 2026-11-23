import { api } from "../client";
import type {
  Account,
  JournalEntry,
  TrialBalance,
} from "@/types/finance";

export const financeApi = {
  async getAccounts(): Promise<Account[]> {
    return api.get<Account[]>("/api/v1/finance/accounts/");
  },

  async createAccount(data: unknown): Promise<{ account_id: string }> {
    return api.post("/api/v1/finance/accounts/", data);
  },

  async getJournalEntries(): Promise<JournalEntry[]> {
    return api.get<JournalEntry[]>("/api/v1/finance/journal-entries/");
  },

  async createJournalEntry(data: unknown): Promise<{ entry_id: string }> {
    return api.post("/api/v1/finance/journal-entries/", data);
  },

  async postJournalEntry(id: string): Promise<void> {
    return api.post(`/api/v1/finance/journal-entries/${id}/post/`, {});
  },

  async getTrialBalance(): Promise<TrialBalance> {
    return api.get<TrialBalance>("/api/v1/finance/reports/trial-balance/");
  },
};
