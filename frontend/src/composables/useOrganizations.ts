import { ref, watch, onMounted, getCurrentInstance } from "vue";
import { organizationsApi } from "@/api/modules/organizations";
import type { CreateBranchPayload, CreateDepartmentPayload } from "@/api/modules/organizations";
import { useTenantStore } from "@/stores/tenant";
import { useToastStore } from "@/stores/toast";
import type { Branch, Department, Member } from "@/types/organization";

export function useOrganizations() {
  const tenantStore = useTenantStore();
  const toastStore = useToastStore();

  const branches = ref<Branch[]>([]);
  const departments = ref<Department[]>([]);
  const members = ref<Member[]>([]);

  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadData() {
    if (!tenantStore.currentOrganizationId) return;
    isLoading.value = true;
    errorMessage.value = null;

    try {
      const [branchRes, deptRes, memberRes] = await Promise.all([
        organizationsApi.getBranches().catch(() => []),
        organizationsApi.getDepartments().catch(() => []),
        organizationsApi.getMembers().catch(() => []),
      ]);
      branches.value = branchRes;
      departments.value = deptRes;
      members.value = memberRes;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load organizational data.";
      toastStore.error(errorMessage.value);
    } finally {
      isLoading.value = false;
    }
  }

  async function createBranch(payload: CreateBranchPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await organizationsApi.createBranch(payload);
      successMessage.value = `Branch "${payload.name}" created successfully.`;
      toastStore.success(successMessage.value);
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value =
        error?.data?.detail || error.message || "Failed to create branch.";
      toastStore.error(errorMessage.value);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createDepartment(payload: CreateDepartmentPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await organizationsApi.createDepartment(payload);
      successMessage.value = `Department "${payload.name}" created successfully.`;
      toastStore.success(successMessage.value);
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value =
        error?.data?.detail || error.message || "Failed to create department.";
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
    branches,
    departments,
    members,
    isLoading,
    errorMessage,
    successMessage,
    loadData,
    createBranch,
    createDepartment,
    clearMessages,
  };
}
