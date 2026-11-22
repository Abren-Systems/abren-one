<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const errorMessage = ref("");

async function onSubmit() {
  if (!username.value || !password.value) {
    errorMessage.value = "Please enter both username and password.";
    return;
  }
  errorMessage.value = "";
  try {
    await authStore.login({
      username: username.value,
      password: password.value,
    });
    router.push({ name: "dashboard" });
  } catch (err: any) {
    errorMessage.value = err?.data?.detail || err?.message || "Invalid credentials.";
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="brand-header">
        <span class="logo-mark">◈</span>
        <h1 class="brand-title">Abren One</h1>
        <p class="brand-subtitle">Nonprofit Operations Platform</p>
      </div>

      <div v-if="errorMessage" class="error-banner" role="alert">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="onSubmit" class="login-form">
        <div class="form-group">
          <label class="form-label" for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-input"
            required
            autocomplete="username"
            autofocus
            placeholder="Enter your username"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            required
            autocomplete="current-password"
            placeholder="••••••••••••"
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary login-btn"
          :disabled="authStore.isLoading"
        >
          {{ authStore.isLoading ? "Signing in..." : "Sign In" }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border-radius: var(--radius-lg);
  padding: 2.5rem 2rem;
  box-shadow: var(--shadow-lg);
}

.brand-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-mark {
  color: var(--color-accent);
  font-size: 2.5rem;
  line-height: 1;
}

.brand-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-top: 0.5rem;
}

.brand-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.error-banner {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.login-btn {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.65rem 1rem;
  font-size: 0.9375rem;
}
</style>
