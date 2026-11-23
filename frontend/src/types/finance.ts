export interface Account {
  id: string;
  code: string;
  name: string;
  account_type: "asset" | "liability" | "equity" | "revenue" | "expense";
  currency: string;
  is_active: boolean;
}

export interface JournalLine {
  id?: string;
  account_id: string;
  account_code?: string;
  account_name?: string;
  debit: string | number;
  credit: string | number;
  memo?: string;
}

export interface JournalEntry {
  id: string;
  entry_number: string;
  entry_date: string;
  memo: string;
  currency: string;
  status: "draft" | "posted" | "reversed";
  total_amount: string;
  reversal_of_id: string | null;
}

export interface TrialBalanceItem {
  account_id: string;
  code: string;
  name: string;
  account_type: string;
  normal_balance: string;
  total_debit: string;
  total_credit: string;
  balance_debit: string;
  balance_credit: string;
}

export interface TrialBalance {
  items: TrialBalanceItem[];
  total_debits: string;
  total_credits: string;
  is_balanced: boolean;
  currency: string;
}

export interface CreateAccountPayload {
  code: string;
  name: string;
  account_type: "asset" | "liability" | "equity" | "revenue" | "expense";
  currency?: string;
  description?: string;
  parent_id?: string | null;
}

export interface CreateJournalLinePayload {
  account_id: string;
  debit: number;
  credit: number;
  memo?: string;
}

export interface CreateJournalEntryPayload {
  entry_date: string;
  memo: string;
  currency?: string;
  post_immediately?: boolean;
  lines: CreateJournalLinePayload[];
  program_id?: string | null;
  grant_id?: string | null;
  donation_id?: string | null;
}

export interface ReverseJournalEntryPayload {
  reason: string;
}
