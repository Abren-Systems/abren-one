import { ref, watch, onMounted, getCurrentInstance } from "vue";
import { procurementApi } from "@/api/modules/procurement";
import { useTenantStore } from "@/stores/tenant";
import type {
  GoodsReceiptNote,
  PurchaseOrder,
  PurchaseRequisition,
  Vendor,
} from "@/types/procurement";

export function useProcurement() {
  const tenantStore = useTenantStore();

  const vendors = ref<Vendor[]>([]);
  const requisitions = ref<PurchaseRequisition[]>([]);
  const orders = ref<PurchaseOrder[]>([]);
  const goodsReceipts = ref<GoodsReceiptNote[]>([]);

  const selectedRequisition = ref<PurchaseRequisition | null>(null);
  const selectedOrder = ref<PurchaseOrder | null>(null);
  const selectedGrn = ref<GoodsReceiptNote | null>(null);

  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadData() {
    if (!tenantStore.currentOrganizationId) return;
    isLoading.value = true;
    errorMessage.value = null;

    try {
      const [vRes, rRes, oRes, grnRes] = await Promise.all([
        procurementApi.getVendors().catch(() => []),
        procurementApi.getRequisitions().catch(() => []),
        procurementApi.getOrders().catch(() => []),
        procurementApi.getGoodsReceipts().catch(() => []),
      ]);

      vendors.value = vRes;
      requisitions.value = rRes;
      orders.value = oRes;
      goodsReceipts.value = grnRes;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load procurement data.";
    } finally {
      isLoading.value = false;
    }
  }

  async function createVendor(data: unknown) {
    isLoading.value = true;
    try {
      const res = await procurementApi.createVendor(data);
      successMessage.value = "Vendor registered successfully.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to create vendor.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deactivateVendor(vendorId: string) {
    isLoading.value = true;
    try {
      await procurementApi.deactivateVendor(vendorId);
      successMessage.value = "Vendor deactivated.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to deactivate vendor.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createRequisition(data: unknown) {
    isLoading.value = true;
    try {
      const res = await procurementApi.createRequisition(data);
      successMessage.value = "Requisition created.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to create requisition.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function submitRequisition(id: string) {
    isLoading.value = true;
    try {
      await procurementApi.submitRequisition(id);
      successMessage.value = "Requisition submitted for approval.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to submit requisition.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function approveRequisition(id: string) {
    isLoading.value = true;
    try {
      await procurementApi.approveRequisition(id);
      successMessage.value = "Requisition approved.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to approve requisition.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function rejectRequisition(id: string, reason: string) {
    isLoading.value = true;
    try {
      await procurementApi.rejectRequisition(id, reason);
      successMessage.value = "Requisition rejected.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to reject requisition.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createOrder(data: unknown) {
    isLoading.value = true;
    try {
      const res = await procurementApi.createOrder(data);
      successMessage.value = "Purchase Order created.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to create purchase order.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function issueOrder(id: string) {
    isLoading.value = true;
    try {
      await procurementApi.issueOrder(id);
      successMessage.value = "Purchase Order issued to vendor.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to issue purchase order.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function cancelOrder(id: string, reason: string) {
    isLoading.value = true;
    try {
      await procurementApi.cancelOrder(id, reason);
      successMessage.value = "Purchase Order cancelled.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to cancel purchase order.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createGoodsReceipt(data: unknown) {
    isLoading.value = true;
    try {
      const res = await procurementApi.createGoodsReceipt(data);
      successMessage.value = "Goods Receipt recorded.";
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to record goods receipt.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function inspectGoodsReceipt(id: string, data: unknown) {
    isLoading.value = true;
    try {
      await procurementApi.inspectGoodsReceipt(id, data);
      successMessage.value = "Goods Receipt inspected.";
      await loadData();
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to inspect goods receipt.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearMessages() {
    errorMessage.value = null;
    successMessage.value = null;
  }

  watch(() => tenantStore.currentOrganizationId, () => {
    loadData();
  });

  if (getCurrentInstance()) {
    onMounted(() => {
      loadData();
    });
  }

  return {
    // State
    vendors,
    requisitions,
    orders,
    goodsReceipts,
    selectedRequisition,
    selectedOrder,
    selectedGrn,
    isLoading,
    errorMessage,
    successMessage,

    // Actions
    loadData,
    createVendor,
    deactivateVendor,
    createRequisition,
    submitRequisition,
    approveRequisition,
    rejectRequisition,
    createOrder,
    issueOrder,
    cancelOrder,
    createGoodsReceipt,
    inspectGoodsReceipt,
    clearMessages,
  };
}
