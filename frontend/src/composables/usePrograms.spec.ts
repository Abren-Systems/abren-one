import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { usePrograms } from "./usePrograms";
import { programsApi } from "@/api/modules/programs";
import { useTenantStore } from "@/stores/tenant";

const mockPrograms = [
  {
    id: "prog-1",
    organization_id: "org-1",
    name: "Health & Nutrition Response",
    description: "Multi-year health program",
    start_date: "2026-01-01",
    end_date: "2026-12-31",
    is_active: true,
    status: "active",
  },
];

const mockProjects = [
  {
    id: "proj-1",
    organization_id: "org-1",
    program_id: "prog-1",
    name: "WASH Infrastructure",
    description: "Water and sanitation",
    budget_currency: "USD",
    status: "active",
  },
];

const mockActivities = [
  {
    id: "act-1",
    organization_id: "org-1",
    project_id: "proj-1",
    name: "Borehole Drilling",
    status: "planned",
  },
];

describe("usePrograms composable", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const tenant = useTenantStore();
    tenant.selectOrganization("org-1");
    vi.restoreAllMocks();
  });

  it("loads programs, projects, and activities", async () => {
    vi.spyOn(programsApi, "getPrograms").mockResolvedValue(mockPrograms);
    vi.spyOn(programsApi, "getProjects").mockResolvedValue(mockProjects);
    vi.spyOn(programsApi, "getActivities").mockResolvedValue(mockActivities);

    const { programs, projects, activities, isLoading, errorMessage, loadData } =
      usePrograms();

    await loadData();

    expect(programs.value.length).toBe(1);
    expect(programs.value[0].name).toBe("Health & Nutrition Response");
    expect(projects.value.length).toBe(1);
    expect(projects.value[0].name).toBe("WASH Infrastructure");
    expect(activities.value.length).toBe(1);
    expect(activities.value[0].name).toBe("Borehole Drilling");
    expect(isLoading.value).toBe(false);
    expect(errorMessage.value).toBeNull();
  });

  it("creates program and refreshes state", async () => {
    const createSpy = vi
      .spyOn(programsApi, "createProgram")
      .mockResolvedValue({ program_id: "prog-new" });
    vi.spyOn(programsApi, "getPrograms").mockResolvedValue([]);
    vi.spyOn(programsApi, "getProjects").mockResolvedValue([]);
    vi.spyOn(programsApi, "getActivities").mockResolvedValue([]);

    const { createProgram, successMessage } = usePrograms();

    await createProgram({
      name: "Emergency Relief",
      description: "Rapid response",
      start_date: "2026-06-01",
      end_date: null,
    });

    expect(createSpy).toHaveBeenCalledWith({
      name: "Emergency Relief",
      description: "Rapid response",
      start_date: "2026-06-01",
      end_date: null,
    });
    expect(successMessage.value).toBe('Program "Emergency Relief" created successfully.');
  });

  it("creates project and refreshes state", async () => {
    const createSpy = vi
      .spyOn(programsApi, "createProject")
      .mockResolvedValue({ project_id: "proj-new" });
    vi.spyOn(programsApi, "getPrograms").mockResolvedValue([]);
    vi.spyOn(programsApi, "getProjects").mockResolvedValue([]);
    vi.spyOn(programsApi, "getActivities").mockResolvedValue([]);

    const { createProject, successMessage } = usePrograms();

    await createProject({
      program_id: "prog-1",
      name: "WASH Infrastructure",
      description: "Water systems",
    });

    expect(createSpy).toHaveBeenCalled();
    expect(successMessage.value).toBe('Project "WASH Infrastructure" created successfully.');
  });

  it("creates activity and refreshes state", async () => {
    const createSpy = vi
      .spyOn(programsApi, "createActivity")
      .mockResolvedValue({ activity_id: "act-new" });
    vi.spyOn(programsApi, "getPrograms").mockResolvedValue([]);
    vi.spyOn(programsApi, "getProjects").mockResolvedValue([]);
    vi.spyOn(programsApi, "getActivities").mockResolvedValue([]);

    const { createActivity, successMessage } = usePrograms();

    await createActivity({
      project_id: "proj-1",
      name: "Borehole Drilling",
    });

    expect(createSpy).toHaveBeenCalled();
    expect(successMessage.value).toBe('Activity "Borehole Drilling" created successfully.');
  });

  it("createProgram throws and sets errorMessage on failure", async () => {
    vi.spyOn(programsApi, "createProgram").mockRejectedValue(
      Object.assign(new Error("Server error"), { data: { detail: "Invalid program name" } })
    );

    const { createProgram, errorMessage } = usePrograms();

    await expect(createProgram({ name: "Bad", description: undefined, start_date: null, end_date: null })).rejects.toThrow();
    expect(errorMessage.value).toBe("Invalid program name");
  });
});
