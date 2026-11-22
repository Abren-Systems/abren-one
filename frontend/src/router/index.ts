import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { requiresGuest: true },
    },
    {
      path: "/",
      name: "dashboard",
      component: () => import("@/views/DashboardView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/organizations",
      name: "organizations",
      component: () => import("@/views/OrganizationsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/programs",
      name: "programs",
      component: () => import("@/views/ProgramsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/fundraising",
      name: "fundraising",
      component: () => import("@/views/FundraisingView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/beneficiaries",
      name: "beneficiaries",
      component: () => import("@/views/BeneficiariesView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/finance",
      name: "finance",
      component: () => import("@/views/FinanceView.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  const tenantStore = useTenantStore();

  // If user state is not loaded yet, fetch profile
  if (authStore.user === null && !authStore.isLoading) {
    await authStore.fetchCurrentUser();
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: "login" });
    return;
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: "dashboard" });
    return;
  }

  // Load organizations if user is authenticated and none loaded
  if (authStore.isAuthenticated && tenantStore.organizations.length === 0) {
    await tenantStore.loadOrganizations();
  }

  next();
});

export default router;
