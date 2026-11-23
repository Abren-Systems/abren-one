import { ref, watch, onMounted, getCurrentInstance } from "vue";
import { beneficiariesApi } from "@/api/modules/beneficiaries";
import { useTenantStore } from "@/stores/tenant";
import { useToastStore } from "@/stores/toast";
import type {
  Beneficiary,
  RecordDeliveryPayload,
  RegisterBeneficiaryPayload,
  ServiceDelivery,
} from "@/types/beneficiary";

export function useBeneficiaries() {
  const tenantStore = useTenantStore();
  const toastStore = useToastStore();

  const beneficiaries = ref<Beneficiary[]>([]);
  const deliveries = ref<ServiceDelivery[]>([]);

  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadData() {
    if (!tenantStore.currentOrganizationId) return;
    isLoading.value = true;
    errorMessage.value = null;

    try {
      const [bRes, dRes] = await Promise.all([
        beneficiariesApi.getBeneficiaries().catch(() => []),
        beneficiariesApi.getDeliveries().catch(() => []),
      ]);
      beneficiaries.value = bRes;
      deliveries.value = dRes;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load beneficiary records.";
      toastStore.error(errorMessage.value);
    } finally {
      isLoading.value = false;
    }
  }

  async function registerBeneficiary(payload: RegisterBeneficiaryPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await beneficiariesApi.registerBeneficiary(payload);
      const name = payload.household_name || `${payload.first_name || ""} ${payload.last_name || ""}`.trim() || "Beneficiary";
      successMessage.value = `Registered "${name}" successfully.`;
      toastStore.success(successMessage.value);
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to register beneficiary.";
      toastStore.error(errorMessage.value);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function recordDelivery(payload: RecordDeliveryPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await beneficiariesApi.recordDelivery(payload);
      successMessage.value = "Service delivery event recorded successfully.";
      toastStore.success(successMessage.value);
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to record service delivery.";
      toastStore.error(errorMessage.value);
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
    beneficiaries,
    deliveries,
    isLoading,
    errorMessage,
    successMessage,
    loadData,
    registerBeneficiary,
    recordDelivery,
    clearMessages,
  };
}
