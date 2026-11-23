import { test, expect } from "@playwright/test";
import { setupMockApi } from "./fixtures";

test.describe("Programs & Projects Lifecycle Workflow", () => {
  test.beforeEach(async ({ page }) => {
    await setupMockApi(page, { authenticated: true });
    await page.goto("/programs");
  });

  test("displays program list with tabs and navigation", async ({ page }) => {
    await expect(page.locator(".page-title")).toHaveText("Program Delivery Hierarchy");
    await expect(page.locator("button:has-text('Strategic Programs')")).toBeVisible();
    await expect(page.locator("button:has-text('Projects')")).toBeVisible();
    await expect(page.locator("button:has-text('Operational Activities')")).toBeVisible();

    // Verify initial program row
    const row = page.locator("tbody tr").first();
    await expect(row).toContainText("Emergency Nutrition & Health");
  });

  test("can filter programs using search box", async ({ page }) => {
    const searchInput = page.locator("input[placeholder*='Search programs']");
    await searchInput.fill("Nutrition");

    await expect(page.locator("tbody tr")).toHaveCount(1);
    await expect(page.locator("tbody tr").first()).toContainText("Emergency Nutrition & Health");

    await searchInput.fill("NonExistentXYZ");
    await expect(page.locator("tbody tr")).toHaveCount(0);
    await expect(page.locator(".empty-container")).toContainText("No Programs Found");
  });

  test("creates a new strategic program via modal with validation and toast", async ({ page }) => {
    await page.locator("button:has-text('+ Create Strategic Program')").first().click();

    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();
    await expect(modal).toContainText("Create Strategic Program");

    // Fill form
    await page.locator("input#prog-name").fill("WASH Emergency Response");
    await page.locator("textarea#prog-desc").fill("Water purification and borehole restoration");
    await page.locator("input#prog-start").fill("2026-03-01");
    await page.locator("input#prog-end").fill("2026-09-30");

    await modal.locator("button:has-text('Create Program')").click();

    // Verify modal closes and toast pops up
    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Program "WASH Emergency Response" created successfully.');

    // Verify newly created program in table
    await expect(page.locator("table")).toContainText("WASH Emergency Response");
  });

  test("can switch tabs between Programs, Projects, and Activities", async ({ page }) => {
    // Switch to Projects
    await page.locator("button:has-text('Projects')").click();
    await expect(page.locator("table")).toContainText("Supplementary Feeding Clinic");

    // Switch to Activities
    await page.locator("button:has-text('Operational Activities')").click();
    await expect(page.locator("table")).toContainText("Community Screenings");
  });
});

