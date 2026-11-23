import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import router from "./index";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";

describe("Router navigation guards", () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    vi.restoreAllMocks();
    await router.push("/login");
  });

  it("redirects unauthenticated users to login for protected routes", async () => {
    const authStore = useAuthStore();
    authStore.user = null;
    vi.spyOn(authStore, "fetchCurrentUser").mockResolvedValue();

    await router.push("/finance");
    expect(router.currentRoute.value.name).toBe("login");
  });

  it("redirects authenticated users from guest-only routes like login to dashboard", async () => {
    const authStore = useAuthStore();
    authStore.user = {
      id: "u1",
      username: "yuma",
      email: "yuma@example.org",
      first_name: "Yuma",
      last_name: "Admin",
      is_staff: true,
      is_superuser: false,
    };

    const tenantStore = useTenantStore();
    vi.spyOn(tenantStore, "loadOrganizations").mockResolvedValue();

    // Start at a protected view first
    await router.push("/programs");
    expect(router.currentRoute.value.name).toBe("programs");

    // Now try navigating to /login while authenticated
    await router.push("/login");
    expect(router.currentRoute.value.name).toBe("dashboard");
  });

  it("allows authenticated users to navigate to protected views", async () => {
    const authStore = useAuthStore();
    authStore.user = {
      id: "u1",
      username: "yuma",
      email: "yuma@example.org",
      first_name: "Yuma",
      last_name: "Admin",
      is_staff: true,
      is_superuser: false,
    };

    const tenantStore = useTenantStore();
    vi.spyOn(tenantStore, "loadOrganizations").mockResolvedValue();

    await router.push("/programs");
    expect(router.currentRoute.value.name).toBe("programs");

    await router.push("/procurement");
    expect(router.currentRoute.value.name).toBe("procurement");
  });
});
