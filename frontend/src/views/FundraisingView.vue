<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { api } from "@/api/client";
import { useTenantStore } from "@/stores/tenant";
import type { Donation, Donor, Grant } from "@/types/fundraising";

const tenantStore = useTenantStore();

const donors = ref<Donor[]>([]);
const grants = ref<Grant[]>([]);
const donations = ref<Donation[]>([]);
const isLoading = ref(false);

// Forms
const newDonorName = ref("");
const newDonorType = ref("foundation");
const newDonorEmail = ref("");

const newDonationDonorId = ref("");
const newDonationAmount = ref("");
const newDonationCurrency = ref("USD");
const newDonationMethod = ref("bank_transfer");

async function loadData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  try {
    const [d, g, don] = await Promise.all([
      api.get<Donor[]>("/api/v1/fundraising/donors/").catch(() => []),
      api.get<Grant[]>("/api/v1/fundraising/grants/").catch(() => []),
      api.get<Donation[]>("/api/v1/fundraising/donations/").catch(() => []),
    ]);
    donors.value = d;
    grants.value = g;
    donations.value = don;

    if (donors.value.length > 0 && !newDonationDonorId.value) {
      newDonationDonorId.value = donors.value[0].id;
    }
  } finally {
    isLoading.value = false;
  }
}

async function createDonor() {
  if (!newDonorName.value) return;
  try {
    await api.post("/api/v1/fundraising/donors/", {
      name: newDonorName.value,
      donor_type: newDonorType.value,
      email: newDonorEmail.value,
    });
    newDonorName.value = "";
    newDonorEmail.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to create donor");
  }
}

async function recordDonation() {
  if (!newDonationDonorId.value || !newDonationAmount.value) return;
  try {
    await api.post("/api/v1/fundraising/donations/", {
      donor_id: newDonationDonorId.value,
      amount: newDonationAmount.value,
      currency: newDonationCurrency.value,
      payment_method: newDonationMethod.value,
    });
    newDonationAmount.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to record donation");
  }
}

async function awardGrant(grantId: string) {
  try {
    await api.post(`/api/v1/fundraising/grants/${grantId}/award/`, {});
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to award grant");
  }
}

async function activateGrant(grantId: string) {
  try {
    await api.post(`/api/v1/fundraising/grants/${grantId}/activate/`, {});
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to activate grant");
  }
}

async function closeGrant(grantId: string) {
  if (!confirm("Are you sure you want to close this grant?")) return;
  try {
    await api.post(`/api/v1/fundraising/grants/${grantId}/close/`, {});
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to close grant");
  }
}

function getGrantBadgeClass(status: string) {
  if (status === "active") return "badge-active";
  if (status === "awarded") return "badge-awarded";
  if (status === "proposed") return "badge-proposed";
  if (status === "closed") return "badge-closed";
  return "";
}

watch(() => tenantStore.currentOrganizationId, () => loadData());
onMounted(() => loadData());
</script>

<template>
  <div class="fundraising-page">
    <div class="page-header">
      <h1 class="page-title">Fundraising & Grant Management</h1>
      <p class="page-subtitle">Track supporters, funding agreements, and incoming contributions.</p>
    </div>

    <!-- Donors Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Supporters & Donors</h3>
        <span class="badge badge-active">{{ donors.length }} Registered</span>
      </div>

      <form @submit.prevent="createDonor" class="inline-form">
        <input v-model="newDonorName" type="text" placeholder="Donor Name (e.g. Global Relief)" class="form-input" required />
        <select v-model="newDonorType" class="form-select select-inline">
          <option value="foundation">Foundation</option>
          <option value="individual">Individual</option>
          <option value="corporation">Corporation</option>
          <option value="government">Government</option>
        </select>
        <input v-model="newDonorEmail" type="email" placeholder="Email" class="form-input" />
        <button type="submit" class="btn btn-primary">Add Donor</button>
      </form>

      <table class="data-table" v-if="donors.length > 0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Email</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in donors" :key="d.id">
            <td><strong>{{ d.name }}</strong></td>
            <td><span class="type-pill">{{ d.donor_type }}</span></td>
            <td>{{ d.email || "–" }}</td>
            <td><span class="badge badge-active">{{ d.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No donors registered yet.</p>
    </section>

    <!-- Grants Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Institutional Grants</h3>
        <span class="badge badge-active">{{ grants.length }} Total</span>
      </div>

      <table class="data-table" v-if="grants.length > 0">
        <thead>
          <tr>
            <th>Grant Title</th>
            <th>Donor</th>
            <th>Reference</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in grants" :key="g.id">
            <td><strong>{{ g.title }}</strong></td>
            <td>{{ g.donor_name }}</td>
            <td><code>{{ g.reference_code }}</code></td>
            <td>{{ g.total_amount }} {{ g.currency }}</td>
            <td><span class="badge" :class="getGrantBadgeClass(g.status)">{{ g.status }}</span></td>
            <td>
              <button
                v-if="g.status === 'proposed'"
                @click="awardGrant(g.id)"
                class="btn-table-action btn-award"
              >
                Award
              </button>
              <button
                v-else-if="g.status === 'awarded'"
                @click="activateGrant(g.id)"
                class="btn-table-action btn-activate"
              >
                Activate
              </button>
              <button
                v-else-if="g.status === 'active'"
                @click="closeGrant(g.id)"
                class="btn-table-action btn-close-grant"
              >
                Close
              </button>
              <span v-else class="text-muted">–</span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No grants awarded yet.</p>
    </section>

    <!-- Donations Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Recorded Donations</h3>
        <span class="badge badge-active">{{ donations.length }} Total</span>
      </div>

      <form @submit.prevent="recordDonation" class="inline-form" v-if="donors.length > 0">
        <select v-model="newDonationDonorId" class="form-select select-inline" required>
          <option v-for="d in donors" :key="d.id" :value="d.id">
            From: {{ d.name }}
          </option>
        </select>
        <input v-model="newDonationAmount" type="number" step="0.01" min="0.01" placeholder="Amount" class="form-input amount-input" required />
        <select v-model="newDonationCurrency" class="form-select curr-input">
          <option value="USD">USD</option>
          <option value="EUR">EUR</option>
          <option value="GBP">GBP</option>
          <option value="ETB">ETB</option>
        </select>
        <button type="submit" class="btn btn-primary">Record Contribution</button>
      </form>

      <table class="data-table" v-if="donations.length > 0">
        <thead>
          <tr>
            <th>Donor</th>
            <th>Amount</th>
            <th>Method</th>
            <th>Received At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="don in donations" :key="don.id">
            <td><strong>{{ don.donor_name }}</strong></td>
            <td>{{ don.amount }} {{ don.currency }}</td>
            <td><span class="type-pill">{{ don.payment_method }}</span></td>
            <td>{{ new Date(don.received_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No donations recorded yet.</p>
    </section>
  </div>
</template>

<style scoped>
.fundraising-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.section-card {
  display: flex;
  flex-direction: column;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.inline-form {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.select-inline {
  max-width: 220px;
}
.amount-input {
  max-width: 140px;
}
.curr-input {
  max-width: 90px;
}
.type-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background-color: #f1f5f9;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: capitalize;
}
.empty-state {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  padding: 1rem 0;
}
.btn-table-action {
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}
.btn-award {
  background-color: #fef3c7;
  color: #92400e;
  border-color: #fde68a;
}
.btn-award:hover {
  background-color: #fde68a;
}
.btn-activate {
  background-color: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}
.btn-activate:hover {
  background-color: #bbf7d0;
}
.btn-close-grant {
  background-color: #fee2e2;
  color: #991b1b;
  border-color: #fecaca;
}
.btn-close-grant:hover {
  background-color: #fecaca;
}
.badge-closed {
  background-color: #f1f5f9;
  color: #64748b;
}
.text-muted {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}
</style>
