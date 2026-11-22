import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api, ApiError, ensureCsrfToken } from "@/api/client";
import type { LoginCredentials, User } from "@/types/auth";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => user.value !== null);

  async function init(): Promise<void> {
    await ensureCsrfToken();
    await fetchCurrentUser();
  }

  async function fetchCurrentUser(): Promise<void> {
    try {
      isLoading.value = true;
      user.value = await api.get<User>("/api/v1/auth/me/");
      error.value = null;
    } catch {
      user.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    try {
      isLoading.value = true;
      error.value = null;
      user.value = await api.post<User>("/api/v1/auth/login/", credentials);
    } catch (err) {
      if (err instanceof ApiError) {
        error.value = err.message;
      } else {
        error.value = "An unexpected error occurred during login.";
      }
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout(): Promise<void> {
    try {
      isLoading.value = true;
      await api.post("/api/v1/auth/logout/");
    } finally {
      user.value = null;
      isLoading.value = false;
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    init,
    fetchCurrentUser,
    login,
    logout,
  };
});
