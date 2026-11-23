<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Number of skeleton rows to render */
    rows?: number;
    /** Show a header skeleton bar above the rows */
    header?: boolean;
    /** Width of the header bar (CSS value) */
    headerWidth?: string;
  }>(),
  {
    rows: 4,
    header: false,
    headerWidth: "40%",
  }
);
</script>

<template>
  <div class="skeleton" aria-hidden="true">
    <div
      v-if="header"
      class="skeleton__bar skeleton__bar--header"
      :style="{ width: headerWidth }"
    />
    <div
      v-for="i in rows"
      :key="i"
      class="skeleton__bar"
      :style="{ width: `${100 - (i % 3) * 12}%` }"
    />
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -400px 0;
  }
  100% {
    background-position: 400px 0;
  }
}

.skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.5rem 0;
  width: 100%;
}

.skeleton__bar {
  height: 1rem;
  border-radius: 4px;
  background: linear-gradient(
    90deg,
    #f1f5f9 25%,
    #e2e8f0 50%,
    #f1f5f9 75%
  );
  background-size: 800px 100%;
  animation: shimmer 1.4s infinite linear;
}

.skeleton__bar--header {
  height: 1.5rem;
  margin-bottom: 0.5rem;
}
</style>
