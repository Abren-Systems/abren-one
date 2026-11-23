<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import AppHeader from "@/components/AppHeader.vue";
import AppNavigation from "@/components/AppNavigation.vue";
import ToastContainer from "@/components/common/ToastContainer.vue";

const route = useRoute();
const isLoginPage = computed(() => route.name === "login");
</script>

<template>
  <div v-if="isLoginPage" class="login-layout">
    <router-view />
  </div>

  <div v-else class="app-layout">
    <AppHeader />
    <div class="layout-body">
      <AppNavigation />
      <main class="main-content" id="main-content">
        <router-view />
      </main>
    </div>
  </div>

  <!-- Global toast notifications — rendered via Teleport to body -->
  <ToastContainer />
</template>

<style scoped>
.login-layout {
  min-height: 100vh;
}

.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-body {
  display: flex;
  flex: 1;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
}
</style>
