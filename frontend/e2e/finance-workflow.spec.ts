import { test, expect } from "@playwright/test";
import { setupMockApi } from "./fixtures";

test.describe("Finance & General Ledger Workflow", () => {
  test.beforeEach(async ({ page }) => {
    await setupMockApi(page, { authenticated: true });
    await page.goto("/finance");
  });

  test("displays chart of accounts and adds a new general ledger account", async ({ page }) => {
    await expect(page.locator(".page-title")).toHaveText("Finance & General Ledger");
    await expect(page.locator("button:has-text('Chart of Accounts')")).toBeVisible();
    await expect(page.locator("button:has-text('Journal Entries')")).toBeVisible();
    await expect(page.locator("button:has-text('Trial Balance')")).toBeVisible();

    await expect(page.locator("table")).toContainText("Cash and Bank Balances");

    // Open Create Account modal
    await page.locator("button:has-text('+ Add Account')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();

    await page.locator("input#acc-code").fill("1020");
    await page.locator("select#acc-type").selectOption("asset");
    await page.locator("input#acc-name").fill("Petty Cash Fund");

    await modal.locator("button:has-text('Create Account')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText("Account 1020 created successfully.");

    await expect(page.locator("table")).toContainText("Petty Cash Fund");
  });

  test("records a double-entry balanced journal entry", async ({ page }) => {
    await page.locator("button:has-text('Journal Entries')").click();
    await expect(page.locator("table")).toContainText("JE-2026-0001");

    // Open Record Journal Entry modal
    await page.locator("button:has-text('+ Record Journal Entry')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();

    await page.locator("input#je-date").fill("2026-02-01");
    await page.locator("input#je-memo").fill("Monthly Bank Service Fee");

    // Line 1: Debit 100
    const rows = modal.locator(".line-row");
    await rows.nth(0).locator("select").selectOption("acc-1");
    await rows.nth(0).locator("input[placeholder='Debit']").fill("100.00");

    // Line 2: Credit 100
    await rows.nth(1).locator("select").selectOption("acc-2");
    await rows.nth(1).locator("input[placeholder='Credit']").fill("100.00");

    // Check balanced indicator
    await expect(modal.locator(".balance-pill")).toContainText("✓ Balanced");

    await modal.locator("button:has-text('Record Entry')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText("Journal entry recorded successfully.");

    await expect(page.locator("table")).toContainText("Monthly Bank Service Fee");
  });

  test("calculates and renders balanced trial balance", async ({ page }) => {
    await page.locator("button:has-text('Trial Balance')").click();

    // Verify trial balance table rendered with summary totals
    await expect(page.locator(".tb-status-badge")).toBeVisible();
    await expect(page.locator(".tb-status-badge.balanced")).toContainText("✓ LEDGER BALANCED");
    await expect(page.locator("table")).toContainText("Cash and Bank Balances");
    await expect(page.locator("table")).toContainText("Grant Revenue");
  });
});

