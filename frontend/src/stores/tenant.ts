import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api, setActiveOrganizationId } from "@/api/client";
import type { UserOrganization } from "@/types/organization";

const STORAGE_KEY = "abren_active_org_id";

export const useTenantStore = defineStore("tenant", () => {
  const organizations = ref<UserOrganization[]>([]);
  const currentOrganizationId = ref<string | null>(
    localStorage.getItem(STORAGE_KEY) || null
  );
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const currentOrganization = computed(() => {
    if (!currentOrganizationId.value) return null;
    return (
      organizations.value.find(
        (o) => o.organization_id === currentOrganizationId.value
      ) || null
    );
  });

  function selectOrganization(orgId: string | null): void {
    currentOrganizationId.value = orgId;
    setActiveOrganizationId(orgId);
    if (orgId) {
      localStorage.setItem(STORAGE_KEY, orgId);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  async function loadOrganizations(): Promise<void> {
    try {
      isLoading.value = true;
      error.value = null;
      organizations.value = await api.get<UserOrganization[]>(
        "/api/v1/organizations/"
      );

      // If active org is stored and valid, ensure it is set
      if (
        currentOrganizationId.value &&
        organizations.value.some(
          (o) => o.organization_id === currentOrganizationId.value
        )
      ) {
        selectOrganization(currentOrganizationId.value);
      } else if (organizations.value.length > 0) {
        // Fallback to first active organization
        const first = organizations.value[0];
        selectOrganization(first.organization_id);
      } else {
        selectOrganization(null);
      }
    } catch (err: any) {
      error.value = err.message || "Failed to load organizations.";
    } finally {
      isLoading.value = false;
    }
  }

  async function provisionOrganization(
    name: string,
    slug: string
  ): Promise<string> {
    try {
      isLoading.value = true;
      const res = await api.post<{ organization_id: string; slug: string }>(
        "/api/v1/organizations/",
        { name, slug }
      );
      await loadOrganizations();
      selectOrganization(res.organization_id);
      return res.organization_id;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    organizations,
    currentOrganizationId,
    currentOrganization,
    isLoading,
    error,
    loadOrganizations,
    selectOrganization,
    provisionOrganization,
  };
});
