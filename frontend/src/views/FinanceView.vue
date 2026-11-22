<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { api } from "@/api/client";
import { useTenantStore } from "@/stores/tenant";
import type { Account, JournalEntry, TrialBalance } from "@/types/finance";

const tenantStore = useTenantStore();

const activeTab = ref<"accounts" | "entries" | "trial_balance">("accounts");
const accounts = ref<Account[]>([]);
const journalEntries = ref<JournalEntry[]>([]);
const trialBalance = ref<TrialBalance | null>(null);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);

// Account form
const newAccountCode = ref("");
const newAccountName = ref("");
const newAccountType = ref<"asset" | "liability" | "equity" | "revenue" | "expense">("asset");
const newAccountCurrency = ref("USD");
const newAccountDescription = ref("");

// Journal Entry form
const newEntryDate = ref(new Date().toISOString().split("T")[0]);
const newEntryMemo = ref("");
const newEntryCurrency = ref("USD");
const newEntryPostImmediately = ref(true);

interface FormLine {
  account_id: string;
  debit: number;
  credit: number;
  memo: string;
}

const formLines = ref<FormLine[]>([
  { account_id: "", debit: 0, credit: 0, memo: "" },
  { account_id: "", debit: 0, credit: 0, memo: "" },
]);

const lineTotalDebits = computed(() => {
  return formLines.value.reduce((acc, l) => acc + (Number(l.debit) || 0), 0);
});

const lineTotalCredits = computed(() => {
  return formLines.value.reduce((acc, l) => acc + (Number(l.credit) || 0), 0);
});

const isFormBalanced = computed(() => {
  return lineTotalDebits.value > 0 && Math.abs(lineTotalDebits.value - lineTotalCredits.value) < 0.001;
});

function addLine() {
  formLines.value.push({ account_id: "", debit: 0, credit: 0, memo: "" });
}

function removeLine(index: number) {
  if (formLines.value.length > 2) {
    formLines.value.splice(index, 1);
  }
}

async function loadData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  errorMessage.value = null;
  try {
    const [accs, entries, tb] = await Promise.all([
      api.get<Account[]>("/api/v1/finance/accounts/"),
      api.get<JournalEntry[]>("/api/v1/finance/journal-entries/"),
      api.get<TrialBalance>("/api/v1/finance/trial-balance/"),
    ]);
    accounts.value = accs;
    journalEntries.value = entries;
    trialBalance.value = tb;

    // Set default accounts for the form if available
    if (accs.length >= 2 && !formLines.value[0].account_id) {
      formLines.value[0].account_id = accs[0].id;
      formLines.value[1].account_id = accs[1].id;
    }
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to load financial records";
  } finally {
    isLoading.value = false;
  }
}

async function handleCreateAccount() {
  if (!tenantStore.currentOrganizationId) return;
  errorMessage.value = null;
  successMessage.value = null;
  try {
    await api.post("/api/v1/finance/accounts/", {
      code: newAccountCode.value.trim(),
      name: newAccountName.value.trim(),
      account_type: newAccountType.value,
      currency: newAccountCurrency.value,
      description: newAccountDescription.value.trim(),
    });
    successMessage.value = `Account ${newAccountCode.value} created successfully.`;
    newAccountCode.value = "";
    newAccountName.value = "";
    newAccountDescription.value = "";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to create account";
  }
}

async function handleCreateEntry() {
  if (!tenantStore.currentOrganizationId) return;
  if (!isFormBalanced.value) {
    errorMessage.value = "Journal entry must be balanced (Debits must equal Credits).";
    return;
  }
  errorMessage.value = null;
  successMessage.value = null;
  try {
    await api.post("/api/v1/finance/journal-entries/", {
      entry_date: newEntryDate.value,
      memo: newEntryMemo.value.trim(),
      currency: newEntryCurrency.value,
      post_immediately: newEntryPostImmediately.value,
      lines: formLines.value.map((l) => ({
        account_id: l.account_id,
        debit: Number(l.debit) || 0,
        credit: Number(l.credit) || 0,
        memo: l.memo.trim(),
      })),
    });
    successMessage.value = "Journal entry recorded successfully.";
    newEntryMemo.value = "";
    formLines.value.forEach((l) => {
      l.debit = 0;
      l.credit = 0;
      l.memo = "";
    });
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to record journal entry";
  }
}

async function handlePostEntry(entryId: string) {
  errorMessage.value = null;
  successMessage.value = null;
  try {
    await api.post(`/api/v1/finance/journal-entries/${entryId}/post/`);
    successMessage.value = "Journal entry posted to general ledger.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to post journal entry";
  }
}

async function handleReverseEntry(entryId: string) {
  const reason = prompt("Please provide a reason for reversing this journal entry:");
  if (!reason) return;
  errorMessage.value = null;
  successMessage.value = null;
  try {
    await api.post(`/api/v1/finance/journal-entries/${entryId}/reverse/`, { reason });
    successMessage.value = "Journal entry reversed with offsetting entry.";
    await loadData();
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to reverse journal entry";
  }
}

watch(() => tenantStore.currentOrganizationId, () => {
  loadData();
});

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="finance-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Finance & General Ledger</h1>
        <p class="page-subtitle">
          Manage chart of accounts, double-entry journal entries, and authoritative trial balance.
        </p>
      </div>

      <div class="tab-controls">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'accounts' }"
          @click="activeTab = 'accounts'"
        >
          Chart of Accounts ({{ accounts.length }})
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'entries' }"
          @click="activeTab = 'entries'"
        >
          Journal Entries ({{ journalEntries.length }})
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'trial_balance' }"
          @click="activeTab = 'trial_balance'"
        >
          Trial Balance
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <!-- Tab 1: Chart of Accounts -->
    <div v-if="activeTab === 'accounts'" class="tab-content">
      <div class="grid-layout">
        <div class="card form-card">
          <h3 class="card-title">Add Account</h3>
          <form @submit.prevent="handleCreateAccount" class="finance-form">
            <div class="form-row">
              <div class="form-group">
                <label>Code (e.g. 1010)</label>
                <input v-model="newAccountCode" placeholder="1010" required />
              </div>
              <div class="form-group">
                <label>Account Type</label>
                <select v-model="newAccountType" required>
                  <option value="asset">Asset (Debit)</option>
                  <option value="liability">Liability (Credit)</option>
                  <option value="equity">Equity (Credit)</option>
                  <option value="revenue">Revenue (Credit)</option>
                  <option value="expense">Expense (Debit)</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Account Name</label>
              <input v-model="newAccountName" placeholder="Operating Cash Account" required />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Currency</label>
                <select v-model="newAccountCurrency">
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="ETB">ETB</option>
                </select>
              </div>
              <div class="form-group">
                <label>Description</label>
                <input v-model="newAccountDescription" placeholder="Optional notes" />
              </div>
            </div>

            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              Create Account
            </button>
          </form>
        </div>

        <div class="card table-card">
          <h3 class="card-title">Active Accounts</h3>
          <div v-if="accounts.length === 0" class="empty-text">
            No accounts in Chart of Accounts yet.
          </div>
          <table v-else class="data-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Name</th>
                <th>Type</th>
                <th>Currency</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="acc in accounts" :key="acc.id">
                <td class="code-cell">{{ acc.code }}</td>
                <td><strong>{{ acc.name }}</strong></td>
                <td>
                  <span class="badge" :class="`badge-${acc.account_type}`">
                    {{ acc.account_type.toUpperCase() }}
                  </span>
                </td>
                <td>{{ acc.currency }}</td>
                <td>
                  <span class="status-tag" :class="{ active: acc.is_active }">
                    {{ acc.is_active ? 'ACTIVE' : 'INACTIVE' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab 2: Journal Entries -->
    <div v-if="activeTab === 'entries'" class="tab-content">
      <div class="card form-card mb-4">
        <h3 class="card-title">Record Balanced Journal Entry</h3>
        <form @submit.prevent="handleCreateEntry" class="journal-form">
          <div class="form-row">
            <div class="form-group">
              <label>Date</label>
              <input type="date" v-model="newEntryDate" required />
            </div>
            <div class="form-group flex-2">
              <label>Memo / Description</label>
              <input v-model="newEntryMemo" placeholder="e.g. Allocation for emergency relief supplies" required />
            </div>
            <div class="form-group">
              <label>Currency</label>
              <select v-model="newEntryCurrency">
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="ETB">ETB</option>
              </select>
            </div>
          </div>

          <div class="lines-section">
            <div class="lines-header">
              <h4>Entry Legs (Debits & Credits)</h4>
              <button type="button" class="btn btn-sm btn-secondary" @click="addLine">
                + Add Leg
              </button>
            </div>

            <div v-for="(line, idx) in formLines" :key="idx" class="line-row">
              <select v-model="line.account_id" class="line-account" required>
                <option value="" disabled>Select Account</option>
                <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                  {{ acc.code }} - {{ acc.name }} ({{ acc.account_type }})
                </option>
              </select>

              <input
                type="number"
                step="0.01"
                min="0"
                v-model.number="line.debit"
                placeholder="Debit"
                class="line-amt"
                @focus="line.credit = 0"
              />

              <input
                type="number"
                step="0.01"
                min="0"
                v-model.number="line.credit"
                placeholder="Credit"
                class="line-amt"
                @focus="line.debit = 0"
              />

              <input
                type="text"
                v-model="line.memo"
                placeholder="Line memo"
                class="line-memo"
              />

              <button
                type="button"
                class="btn-icon"
                @click="removeLine(idx)"
                :disabled="formLines.length <= 2"
                title="Remove line"
              >
                ✕
              </button>
            </div>

            <div class="balance-summary" :class="{ balanced: isFormBalanced, unbalanced: !isFormBalanced }">
              <span>Total Debits: <strong>{{ lineTotalDebits.toFixed(2) }} {{ newEntryCurrency }}</strong></span>
              <span>Total Credits: <strong>{{ lineTotalCredits.toFixed(2) }} {{ newEntryCurrency }}</strong></span>
              <span class="balance-pill">
                {{ isFormBalanced ? '✓ Balanced' : '⚠️ Unbalanced' }}
              </span>
            </div>
          </div>

          <div class="form-actions">
            <label class="checkbox-label">
              <input type="checkbox" v-model="newEntryPostImmediately" />
              <span>Post immediately to ledger</span>
            </label>

            <button type="submit" class="btn btn-primary" :disabled="!isFormBalanced || isLoading">
              Record Entry
            </button>
          </div>
        </form>
      </div>

      <div class="card table-card">
        <h3 class="card-title">General Ledger Entries</h3>
        <div v-if="journalEntries.length === 0" class="empty-text">
          No journal entries recorded yet.
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Entry #</th>
              <th>Date</th>
              <th>Memo</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in journalEntries" :key="entry.id">
              <td class="code-cell">{{ entry.entry_number }}</td>
              <td>{{ entry.entry_date }}</td>
              <td>{{ entry.memo }}</td>
              <td><strong>{{ entry.total_amount }} {{ entry.currency }}</strong></td>
              <td>
                <span class="badge" :class="`badge-${entry.status}`">
                  {{ entry.status.toUpperCase() }}
                </span>
              </td>
              <td>
                <button
                  v-if="entry.status === 'draft'"
                  class="btn btn-xs btn-primary mr-1"
                  @click="handlePostEntry(entry.id)"
                >
                  Post
                </button>
                <button
                  v-if="entry.status === 'posted'"
                  class="btn btn-xs btn-danger"
                  @click="handleReverseEntry(entry.id)"
                >
                  Reverse
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab 3: Live Trial Balance -->
    <div v-if="activeTab === 'trial_balance'" class="tab-content">
      <div class="card">
        <div class="tb-header">
          <div>
            <h3 class="card-title">Trial Balance</h3>
            <p class="tb-subtitle">
              Authoritative summary of posted debits and credits across all accounts.
            </p>
          </div>
          <div
            v-if="trialBalance"
            class="tb-status-badge"
            :class="{ balanced: trialBalance.is_balanced, unbalanced: !trialBalance.is_balanced }"
          >
            {{ trialBalance.is_balanced ? '✓ LEDGER BALANCED' : '⚠️ UNBALANCED' }}
          </div>
        </div>

        <div v-if="!trialBalance || trialBalance.items.length === 0" class="empty-text">
          No posted transactions to calculate trial balance.
        </div>
        <table v-else class="data-table tb-table">
          <thead>
            <tr>
              <th>Account Code</th>
              <th>Account Name</th>
              <th>Type</th>
              <th class="text-right">Debit Balance ({{ trialBalance.currency }})</th>
              <th class="text-right">Credit Balance ({{ trialBalance.currency }})</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in trialBalance.items" :key="item.account_id">
              <td class="code-cell">{{ item.code }}</td>
              <td>{{ item.name }}</td>
              <td>
                <span class="badge" :class="`badge-${item.account_type}`">
                  {{ item.account_type.toUpperCase() }}
                </span>
              </td>
              <td class="text-right font-mono">
                {{ Number(item.balance_debit) > 0 ? item.balance_debit : '—' }}
              </td>
              <td class="text-right font-mono">
                {{ Number(item.balance_credit) > 0 ? item.balance_credit : '—' }}
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td colspan="3"><strong>TOTALS</strong></td>
              <td class="text-right font-mono font-bold">{{ trialBalance.total_debits }}</td>
              <td class="text-right font-mono font-bold">{{ trialBalance.total_credits }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.finance-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
}

.tab-controls {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.grid-layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 1.5rem;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
}

.card-title {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.finance-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.form-group.flex-2 {
  flex: 2;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.form-group input,
.form-group select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.875rem;
  text-align: left;
}

.code-cell {
  font-family: monospace;
  font-weight: bold;
}

.text-right {
  text-align: right;
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: bold;
}

.badge {
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.7rem;
  font-weight: 700;
}

.badge-asset { background: #dbeafe; color: #1e40af; }
.badge-liability { background: #fee2e2; color: #991b1b; }
.badge-equity { background: #fef3c7; color: #92400e; }
.badge-revenue { background: #dcfce7; color: #166534; }
.badge-expense { background: #f3e8ff; color: #6b21a8; }

.badge-draft { background: #f3f4f6; color: #4b5563; }
.badge-posted { background: #dcfce7; color: #166534; }
.badge-reversed { background: #fee2e2; color: #991b1b; }

.status-tag.active {
  color: #16a34a;
  font-weight: 600;
}

/* Journal form styles */
.lines-section {
  margin-top: 1rem;
  background: var(--color-background);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.lines-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.line-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.line-account {
  flex: 3;
  padding: 0.45rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.line-amt {
  flex: 1.5;
  padding: 0.45rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  text-align: right;
}

.line-memo {
  flex: 2;
  padding: 0.45rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #dc2626;
  font-weight: bold;
}

.balance-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0.5rem;
  margin-top: 0.5rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.9rem;
}

.balance-summary.balanced {
  color: #16a34a;
}

.balance-summary.unbalanced {
  color: #dc2626;
}

.balance-pill {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.8rem;
}

.balanced .balance-pill {
  background: #dcfce7;
  color: #166534;
}

.unbalanced .balance-pill {
  background: #fee2e2;
  color: #991b1b;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.tb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.tb-status-badge {
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.85rem;
}

.tb-status-badge.balanced {
  background: #dcfce7;
  color: #166534;
}

.tb-status-badge.unbalanced {
  background: #fee2e2;
  color: #991b1b;
}

.total-row {
  border-top: 2px solid var(--color-text);
  font-size: 1rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #f87171;
}

.alert-success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

.mr-1 {
  margin-right: 0.35rem;
}

.btn-xs {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}
</style>
