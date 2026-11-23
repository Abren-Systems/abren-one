<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useTenantStore } from "@/stores/tenant";
import { programsApi } from "@/api/modules/programs";
import { beneficiariesApi } from "@/api/modules/beneficiaries";
import { fundraisingApi } from "@/api/modules/fundraising";
import { procurementApi } from "@/api/modules/procurement";
import { inventoryApi } from "@/api/modules/inventory";
import SkeletonLoader from "@/components/common/SkeletonLoader.vue";

const tenantStore = useTenantStore();

const programsCount = ref<number | null>(null);
const beneficiariesCount = ref<number | null>(null);
const donorsCount = ref<number | null>(null);
const grantsCount = ref<number | null>(null);
const requisitionsCount = ref<number | null>(null);
const itemsCount = ref<number | null>(null);
const isLoading = ref(false);

async function loadDashboardData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  try {
    const [progs, bens, donors, grants, reqs, items] = await Promise.all([
      programsApi.getPrograms().catch(() => []),
      beneficiariesApi.getBeneficiaries().catch(() => []),
      fundraisingApi.getDonors().catch(() => []),
      fundraisingApi.getGrants().catch(() => []),
      procurementApi.getRequisitions().catch(() => []),
      inventoryApi.getItems().catch(() => []),
    ]);

    programsCount.value = progs.length;
    beneficiariesCount.value = bens.length;
    donorsCount.value = donors.length;
    grantsCount.value = grants.length;
    requisitionsCount.value = reqs.length;
    itemsCount.value = items.length;
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => tenantStore.currentOrganizationId,
  () => {
    loadDashboardData();
  }
);

onMounted(() => {
  loadDashboardData();
});
</script>

<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Operations Overview</h1>
        <p class="page-subtitle" v-if="tenantStore.currentOrganization">
          Active tenant: <strong>{{ tenantStore.currentOrganization.name }}</strong> ({{ tenantStore.currentOrganization.role }})
        </p>
      </div>
    </div>

    <div v-if="!tenantStore.currentOrganizationId" class="empty-banner card">
      <h2>No Organization Selected</h2>
      <p>Please select or provision an organization to access operational records.</p>
    </div>

    <div v-else>
      <div v-if="isLoading && programsCount === null" class="card">
        <SkeletonLoader :rows="3" :header="true" header-width="250px" />
      </div>

      <div v-else class="metrics-grid">
        <div class="card metric-card">
          <span class="metric-icon">🎯</span>
          <div class="metric-info">
            <span class="metric-label">Active Programs</span>
            <span class="metric-val">{{ programsCount ?? "–" }}</span>
          </div>
        </div>

        <div class="card metric-card">
          <span class="metric-icon">🤝</span>
          <div class="metric-info">
            <span class="metric-label">Beneficiaries</span>
            <span class="metric-val">{{ beneficiariesCount ?? "–" }}</span>
          </div>
        </div>

        <div class="card metric-card">
          <span class="metric-icon">🏢</span>
          <div class="metric-info">
            <span class="metric-label">Registered Donors</span>
            <span class="metric-val">{{ donorsCount ?? "–" }}</span>
          </div>
        </div>

        <div class="card metric-card">
          <span class="metric-icon">💰</span>
          <div class="metric-info">
            <span class="metric-label">Active Grants</span>
            <span class="metric-val">{{ grantsCount ?? "–" }}</span>
          </div>
        </div>

        <div class="card metric-card">
          <span class="metric-icon">📦</span>
          <div class="metric-info">
            <span class="metric-label">Procurement Requisitions</span>
            <span class="metric-val">{{ requisitionsCount ?? "–" }}</span>
          </div>
        </div>

        <div class="card metric-card">
          <span class="metric-icon">📊</span>
          <div class="metric-info">
            <span class="metric-label">Tracked Inventory Items</span>
            <span class="metric-val">{{ itemsCount ?? "–" }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Navigation -->
    <div class="quick-nav card" v-if="tenantStore.currentOrganizationId">
      <h3 class="section-title">Core Operating Capabilities</h3>
      <div class="nav-tiles">
        <router-link to="/programs" class="tile">
          <span class="tile-icon">🎯</span>
          <span class="tile-title">Program Delivery</span>
          <span class="tile-desc">Manage strategic programs, projects, and activities</span>
        </router-link>

        <router-link to="/beneficiaries" class="tile">
          <span class="tile-icon">🤝</span>
          <span class="tile-title">Beneficiaries & Services</span>
          <span class="tile-desc">Profiles, vulnerability ratings, and discrete aid deliveries</span>
        </router-link>

        <router-link to="/fundraising" class="tile">
          <span class="tile-icon">💰</span>
          <span class="tile-title">Fundraising & Grants</span>
          <span class="tile-desc">Institutional funding agreements and donations tracking</span>
        </router-link>

        <router-link to="/organizations" class="tile">
          <span class="tile-icon">🏛️</span>
          <span class="tile-title">Structure & Members</span>
          <span class="tile-desc">Branches, departments, and multi-tenant access control</span>
        </router-link>

        <router-link to="/finance" class="tile">
          <span class="tile-icon">📑</span>
          <span class="tile-title">Finance & General Ledger</span>
          <span class="tile-desc">Chart of Accounts, balanced journal entries, and live trial balance</span>
        </router-link>

        <router-link to="/procurement" class="tile">
          <span class="tile-icon">📦</span>
          <span class="tile-title">Procurement & Vendors</span>
          <span class="tile-desc">Purchase requisitions, vendor approvals, and purchase orders</span>
        </router-link>

        <router-link to="/inventory" class="tile">
          <span class="tile-icon">🏭</span>
          <span class="tile-title">Inventory & Warehousing</span>
          <span class="tile-desc">Warehouses, stock receipts, issues, transfers, and ledger movements</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.metric-icon {
  font-size: 2rem;
  background-color: #f1f5f9;
  padding: 0.75rem;
  border-radius: var(--radius-md);
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.metric-val {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.quick-nav {
  margin-top: 0.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.nav-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.tile {
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: inherit;
  transition: all 0.15s ease-in-out;
}

.tile:hover {
  border-color: var(--color-accent);
  background-color: #f8fafc;
  transform: translateY(-2px);
  text-decoration: none;
}

.tile-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.tile-title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--color-text);
}

.tile-desc {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}
</style>
