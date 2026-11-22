<script setup lang="ts">
import { useRoute } from "vue-router";

const route = useRoute();

const navItems = [
  { name: "Overview", path: "/", icon: "📊" },
  { name: "Organizations", path: "/organizations", icon: "🏛️" },
  { name: "Programs & Projects", path: "/programs", icon: "🎯" },
  { name: "Donors & Grants", path: "/fundraising", icon: "💰" },
  { name: "Beneficiaries & Aid", path: "/beneficiaries", icon: "🤝" },
  { name: "Finance & Ledger", path: "/finance", icon: "📑" },
  { name: "Procurement & Purchasing", path: "/procurement", icon: "📦" },
];
</script>

<template>
  <nav class="app-nav" aria-label="Main Navigation">
    <ul class="nav-list">
      <li v-for="item in navItems" :key="item.path">
        <router-link
          :to="item.path"
          class="nav-link"
          :class="{ active: route.path === item.path }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.name }}</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.app-nav {
  width: 240px;
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: 1.5rem 0.75rem;
  display: flex;
  flex-direction: column;
}

.nav-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-weight: 500;
  font-size: 0.875rem;
  text-decoration: none;
  transition: all 0.15s ease-in-out;
}

.nav-link:hover {
  background-color: #f1f5f9;
  color: var(--color-text);
  text-decoration: none;
}

.nav-link.active {
  background-color: #eff6ff;
  color: var(--color-primary);
  font-weight: 600;
}

.nav-icon {
  font-size: 1.125rem;
}
</style>
