<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";

const authStore = useAuthStore();
const tenantStore = useTenantStore();
const router = useRouter();

const showOrgModal = ref(false);
const newOrgName = ref("");
const newOrgSlug = ref("");
const isCreatingOrg = ref(false);

async function handleLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}

function onOrgChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  if (target.value === "__NEW__") {
    showOrgModal.value = true;
    target.value = tenantStore.currentOrganizationId || "";
  } else {
    tenantStore.selectOrganization(target.value);
    window.location.reload(); // Refresh context for views
  }
}

async function createOrg() {
  if (!newOrgName.value.trim() || !newOrgSlug.value.trim()) return;
  try {
    isCreatingOrg.value = true;
    await tenantStore.provisionOrganization(newOrgName.value.trim(), newOrgSlug.value.trim());
    showOrgModal.value = false;
    newOrgName.value = "";
    newOrgSlug.value = "";
    window.location.reload();
  } catch (err: any) {
    alert(err?.message || "Failed to provision organization");
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
    <div v-if="showOrgModal" class="modal-overlay" @click.self="showOrgModal = false">
      <div class="modal-card">
        <h3>Provision New Organization</h3>
        <p class="modal-desc">Create a new organizational tenant boundary.</p>

        <form @submit.prevent="createOrg">
          <div class="form-group">
            <label class="form-label" for="org-name">Organization Name</label>
            <input
              id="org-name"
              v-model="newOrgName"
              type="text"
              class="form-input"
              required
              placeholder="e.g. Sahel Drought Relief"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="org-slug">Slug Identifier</label>
            <input
              id="org-slug"
              v-model="newOrgSlug"
              type="text"
              class="form-input"
              required
              placeholder="e.g. sahel-drought-relief"
            />
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showOrgModal = false"
              :disabled="isCreatingOrg"
            >
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isCreatingOrg">
              {{ isCreatingOrg ? "Creating..." : "Provision Organization" }}
            </button>
          </div>
        </form>
      </div>
    </div>
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  width: 100%;
  max-width: 440px;
  box-shadow: var(--shadow-lg);
}

.modal-desc {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
  margin-bottom: 1.25rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
