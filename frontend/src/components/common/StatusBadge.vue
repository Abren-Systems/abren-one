<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status: string;
}>();

const variant = computed(() => {
  const s = props.status.toLowerCase();
  switch (s) {
    case "active":
    case "awarded":
    case "approved":
    case "fulfilled":
    case "completed":
    case "posted":
    case "received":
    case "inspected":
    case "delivered":
      return "badge-success";

    case "proposed":
    case "draft":
    case "submitted":
    case "planned":
    case "partial":
    case "pending":
      return "badge-warning";

    case "rejected":
    case "cancelled":
    case "suspended":
    case "reversed":
    case "expired":
    case "damaged":
      return "badge-danger";

    case "closed":
    case "inactive":
    case "archived":
    default:
      return "badge-neutral";
  }
});

const label = computed(() => {
  if (!props.status) return "";
  return props.status
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
});
</script>

<template>
  <span class="badge" :class="variant">
    {{ label }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.badge-success {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.badge-warning {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.badge-danger {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.badge-neutral {
  background-color: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}
</style>
