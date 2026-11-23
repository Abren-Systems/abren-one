import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useOrganizations } from "./useOrganizations";
import { organizationsApi } from "@/api/modules/organizations";
import { useTenantStore } from "@/stores/tenant";

const mockBranches = [
  {
    id: "branch-1",
    organization_id: "org-1",
    name: "Headquarters",
    code: "HQ",
    is_headquarters: true,
    is_active: true,
  },
];

const mockDepartments = [
  {
    id: "dept-1",
    organization_id: "org-1",
    branch_id: null,
    name: "Finance",
    code: "FIN",
    is_active: true,
  },
];

const mockMembers = [
  {
    membership_id: "mem-1",
    user_id: "user-1",
    username: "alice",
    email: "alice@example.org",
    role: "admin",
    status: "active",
    is_active: true,
  },
];

describe("useOrganizations composable", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const tenant = useTenantStore();
    tenant.selectOrganization("org-1");
    vi.restoreAllMocks();
  });

  it("loads branches, departments, and members", async () => {
    vi.spyOn(organizationsApi, "getBranches").mockResolvedValue(mockBranches);
    vi.spyOn(organizationsApi, "getDepartments").mockResolvedValue(mockDepartments);
    vi.spyOn(organizationsApi, "getMembers").mockResolvedValue(mockMembers);

    const { branches, departments, members, isLoading, errorMessage, loadData } =
      useOrganizations();

    await loadData();

    expect(branches.value.length).toBe(1);
    expect(branches.value[0].name).toBe("Headquarters");
    expect(departments.value.length).toBe(1);
    expect(departments.value[0].code).toBe("FIN");
    expect(members.value.length).toBe(1);
    expect(members.value[0].username).toBe("alice");
    expect(isLoading.value).toBe(false);
    expect(errorMessage.value).toBeNull();
  });

  it("creates branch and refreshes state", async () => {
    const createSpy = vi
      .spyOn(organizationsApi, "createBranch")
      .mockResolvedValue({ branch_id: "branch-new" });
    vi.spyOn(organizationsApi, "getBranches").mockResolvedValue([]);
    vi.spyOn(organizationsApi, "getDepartments").mockResolvedValue([]);
    vi.spyOn(organizationsApi, "getMembers").mockResolvedValue([]);

    const { createBranch, successMessage } = useOrganizations();

    await createBranch({ name: "Field Office North", code: "FO-N" });

    expect(createSpy).toHaveBeenCalledWith({ name: "Field Office North", code: "FO-N" });
    expect(successMessage.value).toBe('Branch "Field Office North" created successfully.');
  });

  it("creates department and refreshes state", async () => {
    const createSpy = vi
      .spyOn(organizationsApi, "createDepartment")
      .mockResolvedValue({ department_id: "dept-new" });
    vi.spyOn(organizationsApi, "getBranches").mockResolvedValue([]);
    vi.spyOn(organizationsApi, "getDepartments").mockResolvedValue([]);
    vi.spyOn(organizationsApi, "getMembers").mockResolvedValue([]);

    const { createDepartment, successMessage } = useOrganizations();

    await createDepartment({ name: "Logistics", code: "LOG" });

    expect(createSpy).toHaveBeenCalledWith({ name: "Logistics", code: "LOG" });
    expect(successMessage.value).toBe('Department "Logistics" created successfully.');
  });
});
