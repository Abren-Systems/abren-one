import { api } from "../client";
import type {
  Account,
  CreateAccountPayload,
  CreateJournalEntryPayload,
  JournalEntry,
  TrialBalance,
} from "@/types/finance";

export const financeApi = {
  async getAccounts(params?: { account_type?: string; is_active?: boolean }): Promise<Account[]> {
    const query = new URLSearchParams();
    if (params?.account_type) query.append("account_type", params.account_type);
    if (params?.is_active !== undefined) query.append("is_active", String(params.is_active));
    const qs = query.toString();
    return api.get<Account[]>(`/api/v1/finance/accounts/${qs ? `?${qs}` : ""}`);
  },

  async createAccount(data: CreateAccountPayload): Promise<{ account_id: string }> {
    return api.post<{ account_id: string }>("/api/v1/finance/accounts/", data);
  },

  async getJournalEntries(params?: { status?: string }): Promise<JournalEntry[]> {
    const query = new URLSearchParams();
    if (params?.status) query.append("status", params.status);
    const qs = query.toString();
    return api.get<JournalEntry[]>(`/api/v1/finance/journal-entries/${qs ? `?${qs}` : ""}`);
  },

  async createJournalEntry(data: CreateJournalEntryPayload): Promise<{ entry_id: string }> {
    return api.post<{ entry_id: string }>("/api/v1/finance/journal-entries/", data);
  },

  async postJournalEntry(id: string): Promise<void> {
    return api.post<void>(`/api/v1/finance/journal-entries/${id}/post/`, {});
  },

  async reverseJournalEntry(id: string, reason: string): Promise<{ reversal_entry_id: string }> {
    return api.post<{ reversal_entry_id: string }>(`/api/v1/finance/journal-entries/${id}/reverse/`, { reason });
  },

  async getTrialBalance(): Promise<TrialBalance> {
    return api.get<TrialBalance>("/api/v1/finance/trial-balance/");
  },
};
