<script setup lang="ts">
import { ref } from "vue";
import { useFinance } from "@/composables/useFinance";
import type {
  CreateAccountPayload,
  CreateJournalEntryPayload,
  JournalEntry,
} from "@/types/finance";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import AccountsTab from "@/components/finance/tabs/AccountsTab.vue";
import JournalEntriesTab from "@/components/finance/tabs/JournalEntriesTab.vue";
import TrialBalanceTab from "@/components/finance/tabs/TrialBalanceTab.vue";
import CreateAccountModal from "@/components/finance/modals/CreateAccountModal.vue";
import CreateJournalEntryModal from "@/components/finance/modals/CreateJournalEntryModal.vue";
import ReverseJournalEntryModal from "@/components/finance/modals/ReverseJournalEntryModal.vue";

const {
  accounts,
  journalEntries,
  trialBalance,
  isLoading,
  errorMessage,
  successMessage,
  createAccount,
  createJournalEntry,
  postJournalEntry,
  reverseJournalEntry,
  clearMessages,
} = useFinance();

const activeTab = ref<"accounts" | "entries" | "trial_balance">("accounts");

// Modal states
const showCreateAccountModal = ref(false);
const showCreateEntryModal = ref(false);
const showReverseModal = ref(false);
const entryToReverse = ref<JournalEntry | null>(null);

async function handleCreateAccount(payload: CreateAccountPayload) {
  try {
    await createAccount(payload);
    showCreateAccountModal.value = false;
  } catch {
    // Error is already captured in composable errorMessage
  }
}

async function handleCreateEntry(payload: CreateJournalEntryPayload) {
  try {
    await createJournalEntry(payload);
    showCreateEntryModal.value = false;
  } catch {
    // Error is already captured in composable errorMessage
  }
}

async function handlePostEntry(entryId: string) {
  try {
    await postJournalEntry(entryId);
  } catch {
    // Handled in composable
  }
}

function handleOpenReverse(entry: JournalEntry) {
  entryToReverse.value = entry;
  showReverseModal.value = true;
}

async function handleConfirmReverse(entryId: string, reason: string) {
  try {
    await reverseJournalEntry(entryId, reason);
    showReverseModal.value = false;
    entryToReverse.value = null;
  } catch {
    // Handled in composable
  }
}
</script>

<template>
  <div class="finance-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Finance & General Ledger</h1>
        <p class="page-subtitle">
          Manage chart of accounts, double-entry journal entries, and authoritative trial balance.
        </p>
      </div>

      <nav class="tab-controls" aria-label="Finance navigation tabs">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'accounts' }"
          @click="activeTab = 'accounts'"
        >
          Chart of Accounts
          <span class="count-pill">{{ accounts.length }}</span>
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'entries' }"
          @click="activeTab = 'entries'"
        >
          Journal Entries
          <span class="count-pill">{{ journalEntries.length }}</span>
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'trial_balance' }"
          @click="activeTab = 'trial_balance'"
        >
          Trial Balance
          <span
            v-if="trialBalance"
            class="tb-indicator"
            :class="{ balanced: trialBalance.is_balanced, unbalanced: !trialBalance.is_balanced }"
          >
            ●
          </span>
        </button>
      </nav>
    </header>

    <!-- Global Alerts -->
    <div v-if="errorMessage" class="alert alert-error" role="alert">
      <span>{{ errorMessage }}</span>
      <button type="button" class="close-alert" @click="clearMessages">✕</button>
    </div>
    <div v-if="successMessage" class="alert alert-success" role="status">
      <span>{{ successMessage }}</span>
      <button type="button" class="close-alert" @click="clearMessages">✕</button>
    </div>

    <!-- Main Content Area -->
    <main class="page-body">
      <div v-if="isLoading && accounts.length === 0 && journalEntries.length === 0" class="loading-state">
        <LoadingSpinner message="Loading financial records..." />
      </div>

      <div v-else>
        <!-- Tab 1: Chart of Accounts -->
        <AccountsTab
          v-if="activeTab === 'accounts'"
          :accounts="accounts"
          :is-loading="isLoading"
          @open-create-account="showCreateAccountModal = true"
        />

        <!-- Tab 2: Journal Entries -->
        <JournalEntriesTab
          v-if="activeTab === 'entries'"
          :journal-entries="journalEntries"
          :is-loading="isLoading"
          @open-create-entry="showCreateEntryModal = true"
          @post-entry="handlePostEntry"
          @reverse-entry="handleOpenReverse"
        />

        <!-- Tab 3: Trial Balance -->
        <TrialBalanceTab
          v-if="activeTab === 'trial_balance'"
          :trial-balance="trialBalance"
          :is-loading="isLoading"
        />
      </div>
    </main>

    <!-- Modals -->
    <CreateAccountModal
      :open="showCreateAccountModal"
      :is-loading="isLoading"
      @close="showCreateAccountModal = false"
      @create="handleCreateAccount"
    />

    <CreateJournalEntryModal
      :open="showCreateEntryModal"
      :accounts="accounts"
      :is-loading="isLoading"
      @close="showCreateEntryModal = false"
      @create="handleCreateEntry"
    />

    <ReverseJournalEntryModal
      :open="showReverseModal"
      :entry="entryToReverse"
      :is-loading="isLoading"
      @close="showReverseModal = false"
      @confirm="handleConfirmReverse"
    />
  </div>
</template>

<style scoped>
.finance-page {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

.tab-controls {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.85rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #475569;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.tab-btn.active {
  background: #1e3a8a;
  color: #ffffff;
  border-color: #1e3a8a;
}

.count-pill {
  padding: 0.1rem 0.45rem;
  background-color: rgba(0, 0, 0, 0.08);
  border-radius: 9999px;
  font-size: 0.75rem;
}

.tab-btn.active .count-pill {
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.tb-indicator {
  font-size: 0.75rem;
}

.tb-indicator.balanced {
  color: #22c55e;
}

.tb-indicator.unbalanced {
  color: #ef4444;
}

.alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-success {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.close-alert {
  background: transparent;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
}

.close-alert:hover {
  opacity: 1;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 250px;
}
</style>
