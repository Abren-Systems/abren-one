<script setup lang="ts">
import { ref } from "vue";
import { useBeneficiaries } from "@/composables/useBeneficiaries";
import type {
  RecordDeliveryPayload,
  RegisterBeneficiaryPayload,
} from "@/types/beneficiary";

import BeneficiariesTab from "@/components/beneficiaries/tabs/BeneficiariesTab.vue";
import DeliveriesTab from "@/components/beneficiaries/tabs/DeliveriesTab.vue";

import RegisterBeneficiaryModal from "@/components/beneficiaries/modals/RegisterBeneficiaryModal.vue";
import RecordDeliveryModal from "@/components/beneficiaries/modals/RecordDeliveryModal.vue";

const activeTab = ref<"beneficiaries" | "deliveries">("beneficiaries");

const {
  beneficiaries,
  deliveries,
  isLoading,
  errorMessage,
  successMessage,
  registerBeneficiary,
  recordDelivery,
  clearMessages,
} = useBeneficiaries();

const showRegisterModal = ref(false);
const showRecordDeliveryModal = ref(false);

async function handleRegisterBeneficiary(payload: RegisterBeneficiaryPayload) {
  try {
    await registerBeneficiary(payload);
    showRegisterModal.value = false;
  } catch {
    // Handled in composable
  }
}

async function handleRecordDelivery(payload: RecordDeliveryPayload) {
  try {
    await recordDelivery(payload);
    showRecordDeliveryModal.value = false;
  } catch {
    // Handled in composable
  }
}
</script>

<template>
  <div class="beneficiaries-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Beneficiaries & Service Deliveries</h1>
        <p class="page-subtitle">
          Track recipient profiles, vulnerability levels, and direct assistance events.
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
        :class="{ active: activeTab === 'beneficiaries' }"
        @click="activeTab = 'beneficiaries'"
      >
        Registered Profiles ({{ beneficiaries.length }})
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'deliveries' }"
        @click="activeTab = 'deliveries'"
      >
        Service Deliveries ({{ deliveries.length }})
      </button>
    </div>

    <!-- Tab Contents -->
    <div class="tab-content">
      <BeneficiariesTab
        v-if="activeTab === 'beneficiaries'"
        :beneficiaries="beneficiaries"
        :is-loading="isLoading"
        @open-register="showRegisterModal = true"
      />

      <DeliveriesTab
        v-else-if="activeTab === 'deliveries'"
        :deliveries="deliveries"
        :is-loading="isLoading"
        @open-record-delivery="showRecordDeliveryModal = true"
      />
    </div>

    <!-- Modals -->
    <RegisterBeneficiaryModal
      :open="showRegisterModal"
      :is-loading="isLoading"
      @close="showRegisterModal = false"
      @create="handleRegisterBeneficiary"
    />

    <RecordDeliveryModal
      :open="showRecordDeliveryModal"
      :beneficiaries="beneficiaries"
      :is-loading="isLoading"
      @close="showRecordDeliveryModal = false"
      @create="handleRecordDelivery"
    />
  </div>
</template>

<style scoped>
.beneficiaries-view {
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
