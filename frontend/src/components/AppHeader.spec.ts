import { describe, it, expect, beforeEach, vi, beforeAll } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import AppHeader from "./AppHeader.vue";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";

beforeAll(() => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
});

describe("AppHeader.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.restoreAllMocks();
  });

  it("renders brand logo and title", () => {
    const wrapper = mount(AppHeader, {
      global: {
        stubs: {
          RouterLink: { template: "<a><slot /></a>" },
        },
      },
    });

    expect(wrapper.text()).toContain("Abren One");
  });

  it("renders tenant dropdown and user profile when authenticated", () => {
    const authStore = useAuthStore();
    const tenantStore = useTenantStore();

    authStore.user = {
      id: "u1",
      username: "yuma",
      email: "yuma@example.org",
      first_name: "Yuma",
      last_name: "Admin",
      is_staff: true,
      is_superuser: false,
    };

    tenantStore.organizations = [
      {
        organization_id: "org-1",
        name: "Abren Relief",
        slug: "abren-relief",
        role: "owner",
        status: "active",
        is_active: true,
      },
    ];
    tenantStore.selectOrganization("org-1");

    const wrapper = mount(AppHeader, {
      global: {
        stubs: {
          RouterLink: { template: "<a><slot /></a>" },
        },
      },
    });

    expect(wrapper.text()).toContain("Abren Relief (owner)");
    expect(wrapper.text()).toContain("Yuma");
    expect(wrapper.find("select#org-select").exists()).toBe(true);
  });

  it("opens provision modal when '+ Provision New Organization...' is selected", async () => {
    const authStore = useAuthStore();
    const tenantStore = useTenantStore();

    authStore.user = {
      id: "u1",
      username: "yuma",
      email: "yuma@example.org",
      first_name: "Yuma",
      last_name: "Admin",
      is_staff: true,
      is_superuser: false,
    };

    tenantStore.organizations = [
      {
        organization_id: "org-1",
        name: "Abren Relief",
        slug: "abren-relief",
        role: "owner",
        status: "active",
        is_active: true,
      },
    ];
    tenantStore.selectOrganization("org-1");

    const wrapper = mount(AppHeader, {
      global: {
        stubs: {
          RouterLink: { template: "<a><slot /></a>" },
        },
      },
    });

    const select = wrapper.find("select#org-select");
    await select.setValue("__NEW__");

    expect(wrapper.text()).toContain("Provision New Organization");
    expect(wrapper.find("input#org-name").exists()).toBe(true);
    expect(wrapper.find("input#org-slug").exists()).toBe(true);
  });
});
