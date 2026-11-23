<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { useToastStore } from "@/stores/toast";
import ModalDialog from "@/components/common/ModalDialog.vue";

const authStore = useAuthStore();
const tenantStore = useTenantStore();
const toastStore = useToastStore();
const router = useRouter();

const showOrgModal = ref(false);
const newOrgName = ref("");
const newOrgSlug = ref("");
const isCreatingOrg = ref(false);
const orgError = ref<string | null>(null);

async function handleLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}

function onOrgChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  if (target.value === "__NEW__") {
    showOrgModal.value = true;
    orgError.value = null;
    newOrgName.value = "";
    newOrgSlug.value = "";
    target.value = tenantStore.currentOrganizationId || "";
  } else {
    tenantStore.selectOrganization(target.value);
    window.location.reload();
  }
}

function closeOrgModal() {
  showOrgModal.value = false;
  orgError.value = null;
  newOrgName.value = "";
  newOrgSlug.value = "";
}

async function createOrg() {
  if (!newOrgName.value.trim() || !newOrgSlug.value.trim()) return;
  orgError.value = null;
  try {
    isCreatingOrg.value = true;
    await tenantStore.provisionOrganization(newOrgName.value.trim(), newOrgSlug.value.trim());
    toastStore.success(`Organization "${newOrgName.value.trim()}" provisioned successfully.`);
    closeOrgModal();
    window.location.reload();
  } catch (err: any) {
    orgError.value = err?.data?.detail || err?.message || "Failed to provision organization.";
  } finally {
    isCreatingOrg.value = false;
  }
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <router-link to="/" class="brand-logo">
        <span class="logo-mark">◈</span>
        <span class="logo-text">Abren One</span>
      </router-link>
    </div>

    <div class="header-right" v-if="authStore.isAuthenticated">
      <!-- Tenant Selector -->
      <div class="tenant-selector" v-if="tenantStore.organizations.length > 0">
        <label for="org-select" class="sr-only">Active Organization</label>
        <span class="org-icon">🏛️</span>
        <select
          id="org-select"
          class="org-dropdown"
          :value="tenantStore.currentOrganizationId || ''"
          @change="onOrgChange"
        >
          <option
            v-for="org in tenantStore.organizations"
            :key="org.organization_id"
            :value="org.organization_id"
          >
            {{ org.name }} ({{ org.role }})
          </option>
          <option value="__NEW__">+ Provision New Organization...</option>
        </select>
      </div>

      <div class="user-profile">
        <span class="user-name">{{ authStore.user?.first_name || authStore.user?.username }}</span>
        <button type="button" class="btn btn-secondary btn-sm" @click="handleLogout">
          Log Out
        </button>
      </div>
    </div>

    <!-- Provision Org Modal -->
    <ModalDialog :show="showOrgModal" title="Provision New Organization" @close="closeOrgModal">
      <form @submit.prevent="createOrg" class="modal-form">
        <p class="modal-desc">Create a new organizational tenant boundary for your team.</p>

        <div v-if="orgError" class="form-error-banner" role="alert">{{ orgError }}</div>

        <div class="form-group">
          <label class="form-label" for="org-name">Organization Name *</label>
          <input
            id="org-name"
            v-model="newOrgName"
            type="text"
            class="form-input"
            required
            placeholder="e.g. Sahel Drought Relief"
            :disabled="isCreatingOrg"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="org-slug">Slug Identifier *</label>
          <input
            id="org-slug"
            v-model="newOrgSlug"
            type="text"
            class="form-input"
            required
            placeholder="e.g. sahel-drought-relief"
            :disabled="isCreatingOrg"
          />
          <span class="field-hint">Lowercase letters, numbers and hyphens only.</span>
        </div>

        <div class="modal-actions">
          <button
            type="button"
            class="btn btn-secondary"
            @click="closeOrgModal"
            :disabled="isCreatingOrg"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="isCreatingOrg || !newOrgName.trim() || !newOrgSlug.trim()"
          >
            {{ isCreatingOrg ? "Creating..." : "Provision Organization" }}
          </button>
        </div>
      </form>
    </ModalDialog>
  </header>
</template>

<style scoped>
.app-header {
  height: 64px;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  position: sticky;
  top: 0;
  z-index: 40;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--color-primary);
  text-decoration: none;
}

.logo-mark {
  color: var(--color-accent);
  font-size: 1.5rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.tenant-selector {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background-color: #f1f5f9;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.org-dropdown {
  border: none;
  background: transparent;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text);
  cursor: pointer;
  outline: none;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.btn-sm {
  padding: 0.25rem 0.65rem;
  font-size: 0.8125rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-desc {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: -0.25rem;
  margin-bottom: 0.25rem;
}

.form-error-banner {
  background-color: #fef2f2;
  border: 1px solid #fca5a5;
  color: #991b1b;
  border-radius: 6px;
  padding: 0.65rem 0.875rem;
  font-size: 0.875rem;
}

.field-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}
</style>
