import { test, expect } from "@playwright/test";
import { setupMockApi } from "./fixtures";

test.describe("Procurement & Inventory Operations Workflow", () => {
  test.beforeEach(async ({ page }) => {
    await setupMockApi(page, { authenticated: true });
  });

  test("can navigate from dashboard to procurement and view procurement tabs", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(".page-title")).toHaveText("Operations Overview");

    // Click Procurement tile from quick navigation
    await page.locator(".tile[href='/procurement']").click();
    await expect(page).toHaveURL(/.*\/procurement/);
    await expect(page.locator(".page-title")).toHaveText("Procurement & Purchasing");

    // Verify tabs
    await expect(page.locator("button:has-text('Requisitions')")).toBeVisible();
    await expect(page.locator("button:has-text('Purchasing & Orders')")).toBeVisible();
    await expect(page.locator("button:has-text('Goods Receipts')")).toBeVisible();
    await expect(page.locator("button:has-text('Suppliers & Directory')")).toBeVisible();
  });

  test("can navigate from dashboard to inventory and switch inventory views", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(".page-title")).toHaveText("Operations Overview");

    // Click Inventory tile from quick navigation
    await page.locator(".tile[href='/inventory']").click();
    await expect(page).toHaveURL(/.*\/inventory/);
    await expect(page.locator("h1")).toHaveText("Inventory & Stock Management");

    // Verify tabs
    await expect(page.locator("button:has-text('Stock Balances')")).toBeVisible();
    await expect(page.locator("button:has-text('Stock Movements')")).toBeVisible();
    await expect(page.locator("button:has-text('Items & Categories')")).toBeVisible();
    await expect(page.locator("button:has-text('Warehouses & Locations')")).toBeVisible();

    // Switch between tabs
    await page.locator("button:has-text('Stock Movements')").click();
    await expect(page.locator(".inventory-view")).toBeVisible();

    await page.locator("button:has-text('Items & Categories')").click();
    await expect(page.locator(".inventory-view")).toBeVisible();

    await page.locator("button:has-text('Warehouses & Locations')").click();
    await expect(page.locator(".inventory-view")).toBeVisible();
  });
});
