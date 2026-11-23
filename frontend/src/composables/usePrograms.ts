import { ref, watch, onMounted, getCurrentInstance } from "vue";
import { programsApi } from "@/api/modules/programs";
import { useTenantStore } from "@/stores/tenant";
import { useToastStore } from "@/stores/toast";
import type {
  Activity,
  CreateActivityPayload,
  CreateProgramPayload,
  CreateProjectPayload,
  Program,
  Project,
} from "@/types/program";

export function usePrograms() {
  const tenantStore = useTenantStore();
  const toastStore = useToastStore();

  const programs = ref<Program[]>([]);
  const projects = ref<Project[]>([]);
  const activities = ref<Activity[]>([]);

  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);
  const successMessage = ref<string | null>(null);

  async function loadData() {
    if (!tenantStore.currentOrganizationId) return;
    isLoading.value = true;
    errorMessage.value = null;

    try {
      const [progRes, projRes, actRes] = await Promise.all([
        programsApi.getPrograms().catch(() => []),
        programsApi.getProjects().catch(() => []),
        programsApi.getActivities().catch(() => []),
      ]);
      programs.value = progRes;
      projects.value = projRes;
      activities.value = actRes;
    } catch (err: unknown) {
      const error = err as Error;
      errorMessage.value = error.message || "Failed to load program hierarchy.";
      toastStore.error(errorMessage.value);
    } finally {
      isLoading.value = false;
    }
  }

  async function createProgram(payload: CreateProgramPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await programsApi.createProgram(payload);
      successMessage.value = `Program "${payload.name}" created successfully.`;
      toastStore.success(successMessage.value);
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to create program.";
      toastStore.error(errorMessage.value);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createProject(payload: CreateProjectPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await programsApi.createProject(payload);
      successMessage.value = `Project "${payload.name}" created successfully.`;
      toastStore.success(successMessage.value);
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to create project.";
      toastStore.error(errorMessage.value);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createActivity(payload: CreateActivityPayload) {
    isLoading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      const res = await programsApi.createActivity(payload);
      successMessage.value = `Activity "${payload.name}" created successfully.`;
      toastStore.success(successMessage.value);
      await loadData();
      return res;
    } catch (err: unknown) {
      const error = err as any;
      errorMessage.value = error?.data?.detail || error.message || "Failed to create activity.";
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
    programs,
    projects,
    activities,
    isLoading,
    errorMessage,
    successMessage,
    loadData,
    createProgram,
    createProject,
    createActivity,
    clearMessages,
  };
}
