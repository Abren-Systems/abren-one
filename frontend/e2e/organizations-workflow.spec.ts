import { test, expect } from "@playwright/test";
import { setupMockApi } from "./fixtures";

test.describe("Organizational Structure & Members Workflow", () => {
  test.beforeEach(async ({ page }) => {
    await setupMockApi(page, { authenticated: true });
    await page.goto("/organizations");
  });

  test("displays branches list and registers an operational branch", async ({ page }) => {
    await expect(page.locator(".page-title")).toHaveText("Organizational Structure & Members");
    await expect(page.locator("role=tab[name*='Branches']")).toBeVisible();
    await expect(page.locator("role=tab[name*='Departments']")).toBeVisible();
    await expect(page.locator("role=tab[name*='Members']")).toBeVisible();

    await expect(page.locator("table")).toContainText("Country Headquarters");

    // Open Add Branch modal
    await page.locator("button:has-text('+ Add Branch')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();

    await page.locator("input#branch-name").fill("Northern Field Base");
    await page.locator("input#branch-code").fill("nfb-01");

    await modal.locator("button:has-text('Add Branch')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Branch "Northern Field Base" created successfully.');

    await expect(page.locator("table")).toContainText("Northern Field Base");
  });

  test("creates a functional department under Departments tab", async ({ page }) => {
    await page.locator("role=tab[name*='Departments']").click();
    await expect(page.locator("table")).toContainText("Programs & Operations");

    // Open Add Department modal
    await page.locator("button:has-text('+ Add Department')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();

    await page.locator("input#dept-name").fill("Logistics & Fleet");
    await page.locator("input#dept-code").fill("log");

    await modal.locator("button:has-text('Add Department')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Department "Logistics & Fleet" created successfully.');

    await expect(page.locator("table")).toContainText("Logistics & Fleet");
  });

  test("views team memberships and role pills under Members tab", async ({ page }) => {
    await page.locator("role=tab[name*='Members']").click();
    await expect(page.locator("table")).toContainText("admin");
    await expect(page.locator("table")).toContainText("admin@abren.org");
    await expect(page.locator(".role-pill")).toHaveText("owner");
  });
});
