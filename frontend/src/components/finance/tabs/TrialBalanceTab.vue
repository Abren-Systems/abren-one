<script setup lang="ts">
import type { TrialBalance } from "@/types/finance";
import EmptyState from "@/components/common/EmptyState.vue";

defineProps<{
  trialBalance: TrialBalance | null;
  isLoading?: boolean;
}>();
</script>

<template>
  <div class="trial-balance-tab">
    <div v-if="!trialBalance || trialBalance.items.length === 0" class="empty-container">
      <EmptyState
        title="No Trial Balance Data"
        message="No posted journal entries have been recorded yet. The trial balance is calculated from authoritative posted ledger transactions."
      />
    </div>

    <div v-else class="card tb-card">
      <div class="tb-header">
        <div>
          <h3 class="card-title">Authoritative Trial Balance</h3>
          <p class="tb-subtitle">
            Cumulative posted debits and credits across all active accounts.
          </p>
        </div>
        <div
          class="tb-status-badge"
          :class="{
            balanced: trialBalance.is_balanced,
            unbalanced: !trialBalance.is_balanced,
          }"
        >
          {{ trialBalance.is_balanced ? "✓ LEDGER BALANCED" : "⚠️ UNBALANCED" }}
        </div>
      </div>

      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Account Code</th>
              <th>Account Name</th>
              <th>Type</th>
              <th class="text-right">Debit Balance ({{ trialBalance.currency }})</th>
              <th class="text-right">Credit Balance ({{ trialBalance.currency }})</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in trialBalance.items" :key="item.account_id">
              <td class="code-cell">{{ item.code }}</td>
              <td><strong>{{ item.name }}</strong></td>
              <td>
                <span class="type-pill" :class="`type-${item.account_type}`">
                  {{ item.account_type.toUpperCase() }}
                </span>
              </td>
              <td class="text-right font-mono">
                {{ Number(item.balance_debit) > 0 ? item.balance_debit : "—" }}
              </td>
              <td class="text-right font-mono">
                {{ Number(item.balance_credit) > 0 ? item.balance_credit : "—" }}
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td colspan="3"><strong>TOTALS</strong></td>
              <td class="text-right font-mono font-bold">
                {{ trialBalance.total_debits }} {{ trialBalance.currency }}
              </td>
              <td class="text-right font-mono font-bold">
                {{ trialBalance.total_credits }} {{ trialBalance.currency }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trial-balance-tab {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.tb-card {
  display: flex;
  flex-direction: column;
}

.tb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.tb-subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.8125rem;
  color: #64748b;
}

.tb-status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.tb-status-badge.balanced {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.tb-status-badge.unbalanced {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th {
  background-color: #f8fafc;
  color: #475569;
  text-align: left;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
}

.data-table tr:hover {
  background-color: #f8fafc;
}

.code-cell {
  font-family: monospace;
  font-weight: 600;
  color: #1e3a8a;
}

.type-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.type-asset {
  background-color: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.type-liability {
  background-color: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
}

.type-equity {
  background-color: #faf5ff;
  color: #7e22ce;
  border: 1px solid #e9d5ff;
}

.type-revenue {
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.type-expense {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.text-right {
  text-align: right;
}

.font-mono {
  font-family: monospace;
}

.font-bold {
  font-weight: 700;
}

.total-row {
  background-color: #f8fafc;
  border-top: 2px solid #cbd5e1;
}

.total-row td {
  padding: 1rem 1.25rem;
  color: #0f172a;
}

.empty-container {
  padding: 2rem 0;
}
</style>
