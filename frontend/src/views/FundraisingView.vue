<script setup lang="ts">
import { ref } from "vue";
import { useFundraising } from "@/composables/useFundraising";
import type {
  CreateDonorPayload,
  CreateGrantPayload,
  RecordDonationPayload,
} from "@/types/fundraising";

import DonorsTab from "@/components/fundraising/tabs/DonorsTab.vue";
import GrantsTab from "@/components/fundraising/tabs/GrantsTab.vue";
import DonationsTab from "@/components/fundraising/tabs/DonationsTab.vue";

import CreateDonorModal from "@/components/fundraising/modals/CreateDonorModal.vue";
import CreateGrantModal from "@/components/fundraising/modals/CreateGrantModal.vue";
import RecordDonationModal from "@/components/fundraising/modals/RecordDonationModal.vue";

const activeTab = ref<"donors" | "grants" | "donations">("donors");

const {
  donors,
  grants,
  donations,
  isLoading,
  errorMessage,
  successMessage,
  createDonor,
  createGrant,
  awardGrant,
  activateGrant,
  closeGrant,
  recordDonation,
  clearMessages,
} = useFundraising();

// Modal visibility flags
const showCreateDonorModal = ref(false);
const showCreateGrantModal = ref(false);
const showRecordDonationModal = ref(false);

async function handleCreateDonor(payload: CreateDonorPayload) {
  try {
    await createDonor(payload);
    showCreateDonorModal.value = false;
  } catch {
    // Handled in composable
  }
}

async function handleCreateGrant(payload: CreateGrantPayload) {
  try {
    await createGrant(payload);
    showCreateGrantModal.value = false;
  } catch {
    // Handled in composable
  }
}

async function handleRecordDonation(payload: RecordDonationPayload) {
  try {
    await recordDonation(payload);
    showRecordDonationModal.value = false;
  } catch {
    // Handled in composable
  }
}

async function handleAwardGrant(grantId: string) {
  try {
    await awardGrant(grantId);
  } catch {
    // Handled in composable
  }
}

async function handleActivateGrant(grantId: string) {
  try {
    await activateGrant(grantId);
  } catch {
    // Handled in composable
  }
}

async function handleCloseGrant(grantId: string) {
  if (!confirm("Are you sure you want to close this grant?")) return;
  try {
    await closeGrant(grantId);
  } catch {
    // Handled in composable
  }
}
</script>

<template>
  <div class="fundraising-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Fundraising & Grant Management</h1>
        <p class="page-subtitle">
          Track supporters, funding agreements, and incoming contributions.
        </p>
      </div>
    </div>

    <!-- Feedback messages -->
    <div v-if="errorMessage" class="alert alert-error">
      <span>{{ errorMessage }}</span>
      <button type="button" class="alert-close" @click="clearMessages">✕</button>
    </div>

    <div v-if="successMessage" class="alert alert-success">
      <span>{{ successMessage }}</span>
      <button type="button" class="alert-close" @click="clearMessages">✕</button>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-nav">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'donors' }"
        @click="activeTab = 'donors'"
      >
        Supporters & Donors ({{ donors.length }})
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'grants' }"
        @click="activeTab = 'grants'"
      >
        Institutional Grants ({{ grants.length }})
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'donations' }"
        @click="activeTab = 'donations'"
      >
        Recorded Donations ({{ donations.length }})
      </button>
    </div>

    <!-- Tab Contents -->
    <div class="tab-content">
      <DonorsTab
        v-if="activeTab === 'donors'"
        :donors="donors"
        :is-loading="isLoading"
        @open-create-donor="showCreateDonorModal = true"
      />

      <GrantsTab
        v-else-if="activeTab === 'grants'"
        :grants="grants"
        :is-loading="isLoading"
        @open-create-grant="showCreateGrantModal = true"
        @award-grant="handleAwardGrant"
        @activate-grant="handleActivateGrant"
        @close-grant="handleCloseGrant"
      />

      <DonationsTab
        v-else-if="activeTab === 'donations'"
        :donations="donations"
        :is-loading="isLoading"
        @open-record-donation="showRecordDonationModal = true"
      />
    </div>

    <!-- Modals -->
    <CreateDonorModal
      :open="showCreateDonorModal"
      :is-loading="isLoading"
      @close="showCreateDonorModal = false"
      @create="handleCreateDonor"
    />

    <CreateGrantModal
      :open="showCreateGrantModal"
      :donors="donors"
      :is-loading="isLoading"
      @close="showCreateGrantModal = false"
      @create="handleCreateGrant"
    />

    <RecordDonationModal
      :open="showRecordDonationModal"
      :donors="donors"
      :grants="grants"
      :is-loading="isLoading"
      @close="showRecordDonationModal = false"
      @create="handleRecordDonation"
    />
  </div>
</template>

<style scoped>
.fundraising-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.tabs-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.tab-btn {
  background: transparent;
  border: none;
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--color-text);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  display: flex;
  flex-direction: column;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.alert-close {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: inherit;
  opacity: 0.7;
}

.alert-close:hover {
  opacity: 1;
}
</style>
