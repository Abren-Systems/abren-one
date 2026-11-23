import { ref, watch, onMounted, getCurrentInstance } from "vue";
import { fundraisingApi } from "@/api/modules/fundraising";
import { useTenantStore } from "@/stores/tenant";
import type {
  CreateDonorPayload,
  CreateGrantPayload,
  Donation,
  Donor,
  Grant,
  RecordDonationPayload,
} from "@/types/fundraising";

export function useFundraising() {
  const tenantStore = useTenantStore();

  const donors = ref<Donor[]>([]);
  const grants = ref<Grant[]>([]);
  const donations = ref<Donation[]>([]);

  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadData() {
    if (!tenantStore.currentOrganizationId) return;
    isLoading.value = true;
    errorMessage.value = null;

    try {
      const [d, g, don] = await Promise.all([
        fundraisingApi.getDonors().catch(() => []),
        fundraisingApi.getGrants().catch(() => []),
        fundraisingApi.getDonations().catch(() => []),
      ]);
      donors.value = d;
      grants.value = g;
      donations.value = don;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load fundraising data.";
    } finally {
      isLoading.value = false;
    }
  }

  async function createDonor(data: CreateDonorPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await fundraisingApi.createDonor(data);
      successMessage.value = `Donor "${data.name}" added successfully.`;
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to add donor.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createGrant(data: CreateGrantPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await fundraisingApi.createGrant(data);
      successMessage.value = `Grant "${data.title}" registered successfully.`;
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to register grant.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function awardGrant(id: string, notes?: string) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await fundraisingApi.awardGrant(id, notes);
      successMessage.value = "Grant awarded successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to award grant.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function activateGrant(id: string, notes?: string) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await fundraisingApi.activateGrant(id, notes);
      successMessage.value = "Grant activated for program implementation.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to activate grant.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function closeGrant(id: string, reason?: string) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await fundraisingApi.closeGrant(id, reason);
      successMessage.value = "Grant closed successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to close grant.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function recordDonation(data: RecordDonationPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await fundraisingApi.recordDonation(data);
      successMessage.value = "Donation contribution recorded successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to record donation.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearMessages() {
    errorMessage.value = null;
    successMessage.value = null;
  }

  watch(
    () => tenantStore.currentOrganizationId,
    () => {
      loadData();
    }
  );

  if (getCurrentInstance()) {
    onMounted(() => {
      loadData();
    });
  }

  return {
    donors,
    grants,
    donations,
    isLoading,
    errorMessage,
    successMessage,
    loadData,
    createDonor,
    createGrant,
    awardGrant,
    activateGrant,
    closeGrant,
    recordDonation,
    clearMessages,
  };
}
