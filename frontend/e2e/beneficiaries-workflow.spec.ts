import { test, expect } from "@playwright/test";
import { setupMockApi } from "./fixtures";

test.describe("Beneficiaries & Service Deliveries Workflow", () => {
  test.beforeEach(async ({ page }) => {
    await setupMockApi(page, { authenticated: true });
    await page.goto("/beneficiaries");
  });

  test("displays registered beneficiaries and allows search filtering", async ({ page }) => {
    await expect(page.locator(".page-title")).toHaveText("Beneficiaries & Service Deliveries");
    await expect(page.locator("button:has-text('Registered Profiles')")).toBeVisible();
    await expect(page.locator("button:has-text('Service Deliveries')")).toBeVisible();

    const row = page.locator("tbody tr").first();
    await expect(row).toContainText("Fatima Zahra");
    await expect(row).toContainText("ID-90812");

    // Filter by vulnerability or name
    const search = page.locator("input[type='search']");
    await search.fill("Fatima");
    await expect(page.locator("tbody tr")).toHaveCount(1);
  });

  test("registers a new individual beneficiary with modal dialog and toast", async ({ page }) => {
    await page.locator("button:has-text('+ Register Beneficiary')").first().click();

    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();
    await expect(modal).toContainText("Register Beneficiary");

    // Fill form
    await page.locator("input#first-name").fill("Ibrahim");
    await page.locator("input#last-name").fill("Ali");
    await page.locator("input#id-number").fill("ID-44510");
    await page.locator("select#ben-vuln").selectOption("critical");

    await modal.locator("button:has-text('Register Beneficiary')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Registered "Ibrahim Ali" successfully.');

    await expect(page.locator("table")).toContainText("Ibrahim Ali");
  });

  test("records a service delivery event under the Deliveries tab", async ({ page }) => {
    await page.locator("button:has-text('Service Deliveries')").click();
    await expect(page.locator("table")).toContainText("Fatima Zahra");
    await expect(page.locator("table")).toContainText("25 kg");

    // Open Record Service Delivery modal
    await page.locator("button:has-text('+ Record Aid Delivery')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();
    await expect(modal).toContainText("Record Aid Distribution Event");

    // Select beneficiary and fill quantity
    await page.locator("select#del-ben").selectOption("ben-1");
    await page.locator("input#del-qty").fill("50");
    await page.locator("input#del-unit").fill("liters");

    await modal.locator("button:has-text('Record Distribution')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText("Service delivery event recorded successfully.");

    await expect(page.locator("table")).toContainText("50 liters");
  });
});

