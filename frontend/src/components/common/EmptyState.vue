<script setup lang="ts">
defineProps<{
  title: string;
  message?: string;
}>();
</script>

<template>
  <div class="empty-state-card">
    <div class="empty-state-icon" aria-hidden="true">
      <slot name="icon">
        <span>📂</span>
      </slot>
    </div>
    <h3 class="empty-state-title">{{ title }}</h3>
    <p v-if="message" class="empty-state-message">{{ message }}</p>
    <div v-if="$slots.action" class="empty-state-action">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<style scoped>
.empty-state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1.5rem;
  background-color: #fafbfc;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
  margin: 1.5rem 0;
}

.empty-state-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  opacity: 0.7;
}

.empty-state-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.empty-state-message {
  margin: 0.5rem 0 1.25rem 0;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  max-width: 420px;
}

.empty-state-action {
  display: flex;
  gap: 0.5rem;
}
</style>
