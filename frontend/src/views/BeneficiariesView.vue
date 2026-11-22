<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { api } from "@/api/client";
import { useTenantStore } from "@/stores/tenant";
import type { Beneficiary, ServiceDelivery } from "@/types/beneficiary";

const tenantStore = useTenantStore();

const beneficiaries = ref<Beneficiary[]>([]);
const deliveries = ref<ServiceDelivery[]>([]);
const isLoading = ref(false);

// Forms
const benType = ref<"individual" | "household" | "community">("individual");
const firstName = ref("");
const lastName = ref("");
const householdName = ref("");
const idNumber = ref("");
const vulnLevel = ref("medium");

const deliveryBenId = ref("");
const deliveryType = ref("food_assistance");
const deliveryQty = ref("1.00");
const deliveryUnit = ref("unit");
const deliveryDate = ref(new Date().toISOString().split("T")[0]);

async function loadData() {
  if (!tenantStore.currentOrganizationId) return;
  isLoading.value = true;
  try {
    const [b, d] = await Promise.all([
      api.get<Beneficiary[]>("/api/v1/beneficiaries/").catch(() => []),
      api.get<ServiceDelivery[]>("/api/v1/beneficiaries/deliveries/").catch(() => []),
    ]);
    beneficiaries.value = b;
    deliveries.value = d;

    if (beneficiaries.value.length > 0 && !deliveryBenId.value) {
      deliveryBenId.value = beneficiaries.value[0].id;
    }
  } finally {
    isLoading.value = false;
  }
}

async function registerBeneficiary() {
  try {
    await api.post("/api/v1/beneficiaries/", {
      beneficiary_type: benType.value,
      first_name: firstName.value,
      last_name: lastName.value,
      household_name: householdName.value,
      identification_number: idNumber.value,
      vulnerability_level: vulnLevel.value,
    });
    firstName.value = "";
    lastName.value = "";
    householdName.value = "";
    idNumber.value = "";
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to register beneficiary");
  }
}

async function recordDelivery() {
  if (!deliveryBenId.value || !deliveryQty.value) return;
  try {
    await api.post("/api/v1/beneficiaries/deliveries/", {
      beneficiary_id: deliveryBenId.value,
      service_type: deliveryType.value,
      delivery_date: deliveryDate.value,
      quantity: deliveryQty.value,
      unit: deliveryUnit.value,
    });
    await loadData();
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || "Failed to record delivery");
  }
}

watch(() => tenantStore.currentOrganizationId, () => loadData());
onMounted(() => loadData());
</script>

<template>
  <div class="bens-page">
    <div class="page-header">
      <h1 class="page-title">Beneficiaries & Service Deliveries</h1>
      <p class="page-subtitle">Track recipient profiles, vulnerability levels, and direct assistance events.</p>
    </div>

    <!-- Register Beneficiary Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Registered Beneficiaries</h3>
        <span class="badge badge-active">{{ beneficiaries.length }} Profiles</span>
      </div>

      <form @submit.prevent="registerBeneficiary" class="beneficiary-form">
        <div class="form-row">
          <select v-model="benType" class="form-select">
            <option value="individual">Individual</option>
            <option value="household">Household</option>
            <option value="community">Community</option>
          </select>

          <input
            v-if="benType === 'household'"
            v-model="householdName"
            type="text"
            placeholder="Household Name (e.g. Warsame Family)"
            class="form-input"
            required
          />
          <template v-else>
            <input v-model="firstName" type="text" placeholder="First Name" class="form-input" required />
            <input v-model="lastName" type="text" placeholder="Last Name" class="form-input" required />
          </template>

          <input v-model="idNumber" type="text" placeholder="ID / Ration Card #" class="form-input id-input" />
          <select v-model="vulnLevel" class="form-select vuln-select">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <button type="submit" class="btn btn-primary">Register</button>
        </div>
      </form>

      <table class="data-table" v-if="beneficiaries.length > 0">
        <thead>
          <tr>
            <th>Name / Household</th>
            <th>Type</th>
            <th>ID Number</th>
            <th>Vulnerability</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in beneficiaries" :key="b.id">
            <td><strong>{{ b.display_name }}</strong></td>
            <td><span class="type-pill">{{ b.beneficiary_type }}</span></td>
            <td><code>{{ b.identification_number || "–" }}</code></td>
            <td><span class="vuln-badge" :class="'vuln-' + b.vulnerability_level">{{ b.vulnerability_level }}</span></td>
            <td><span class="badge badge-active">{{ b.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No beneficiaries registered yet.</p>
    </section>

    <!-- Service Deliveries Section -->
    <section class="card section-card">
      <div class="card-header">
        <h3>Service Deliveries</h3>
        <span class="badge badge-active">{{ deliveries.length }} Events</span>
      </div>

      <form @submit.prevent="recordDelivery" class="inline-form" v-if="beneficiaries.length > 0">
        <select v-model="deliveryBenId" class="form-select select-inline" required>
          <option v-for="b in beneficiaries" :key="b.id" :value="b.id">
            To: {{ b.display_name }}
          </option>
        </select>
        <select v-model="deliveryType" class="form-select select-inline">
          <option value="food_assistance">Food Assistance</option>
          <option value="medical_support">Medical Support</option>
          <option value="cash_transfer">Cash Transfer</option>
          <option value="education_training">Education & Training</option>
          <option value="shelter_wash">Shelter / WASH</option>
        </select>
        <input v-model="deliveryQty" type="number" step="0.01" min="0" placeholder="Qty" class="form-input qty-input" required />
        <input v-model="deliveryUnit" type="text" placeholder="Unit (kg/kits)" class="form-input unit-input" required />
        <button type="submit" class="btn btn-primary">Record Delivery</button>
      </form>

      <table class="data-table" v-if="deliveries.length > 0">
        <thead>
          <tr>
            <th>Beneficiary</th>
            <th>Service Type</th>
            <th>Quantity</th>
            <th>Delivery Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in deliveries" :key="d.id">
            <td><strong>{{ d.beneficiary_name }}</strong></td>
            <td><span class="type-pill">{{ d.service_type }}</span></td>
            <td>{{ d.quantity }} {{ d.unit }}</td>
            <td>{{ d.delivery_date }}</td>
            <td><span class="badge badge-active">{{ d.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No deliveries recorded yet.</p>
    </section>
  </div>
</template>

<style scoped>
.bens-page {
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
.beneficiary-form {
  margin-bottom: 1rem;
}
.form-row {
  display: flex;
  gap: 0.75rem;
}
.inline-form {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.id-input {
  max-width: 160px;
}
.vuln-select {
  max-width: 130px;
}
.qty-input {
  max-width: 100px;
}
.unit-input {
  max-width: 110px;
}
.select-inline {
  max-width: 220px;
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
.vuln-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}
.vuln-low {
  background-color: #e0f2fe;
  color: #0369a1;
}
.vuln-medium {
  background-color: #fef3c7;
  color: #92400e;
}
.vuln-high {
  background-color: #ffedd5;
  color: #c2410c;
}
.vuln-critical {
  background-color: #fee2e2;
  color: #991b1b;
}
.empty-state {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  padding: 1rem 0;
}
</style>
