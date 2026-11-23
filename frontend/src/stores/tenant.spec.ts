import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useTenantStore } from "./tenant";
import { getActiveOrganizationId } from "@/api/client";

describe("Tenant Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it("selects an organization and syncs with API client and localStorage", () => {
    const store = useTenantStore();
    expect(store.currentOrganizationId).toBeNull();
    expect(store.currentOrganization).toBeNull();

    store.selectOrganization("org-999");
    expect(store.currentOrganizationId).toBe("org-999");
    expect(getActiveOrganizationId()).toBe("org-999");
    expect(localStorage.getItem("abren_active_org_id")).toBe("org-999");

    store.selectOrganization(null);
    expect(store.currentOrganizationId).toBeNull();
    expect(getActiveOrganizationId()).toBeNull();
    expect(localStorage.getItem("abren_active_org_id")).toBeNull();
  });

  it("computes currentOrganization from organizations list", () => {
    const store = useTenantStore();
    store.organizations = [
      {
        organization_id: "org-1",
        name: "First Org",
        slug: "first-org",
        role: "owner",
        status: "active",
        is_active: true,
      },
      {
        organization_id: "org-2",
        name: "Second Org",
        slug: "second-org",
        role: "member",
        status: "active",
        is_active: true,
      },
    ];

    store.selectOrganization("org-2");
    expect(store.currentOrganization).toBeDefined();
    expect(store.currentOrganization?.name).toBe("Second Org");
    expect(store.currentOrganization?.role).toBe("member");
  });
});
