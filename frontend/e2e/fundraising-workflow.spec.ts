import { test, expect } from "@playwright/test";
import { setupMockApi } from "./fixtures";

test.describe("Fundraising, Grants & Donations Workflow", () => {
  test.beforeEach(async ({ page }) => {
    await setupMockApi(page, { authenticated: true });
    await page.goto("/fundraising");
  });

  test("displays donors list and adds a new donor organization", async ({ page }) => {
    await expect(page.locator(".page-title")).toHaveText("Fundraising & Grant Management");
    await expect(page.locator("button:has-text('Supporters & Donors')")).toBeVisible();
    await expect(page.locator("button:has-text('Institutional Grants')")).toBeVisible();
    await expect(page.locator("button:has-text('Recorded Donations')")).toBeVisible();

    await expect(page.locator("table")).toContainText("Global Food Assistance Fund");

    // Open Add Donor modal
    await page.locator("button:has-text('+ Add Supporter / Donor')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();

    await page.locator("input#donor-name").fill("Nordic Humanitarian Agency");
    await page.locator("select#donor-type").selectOption("government");
    await page.locator("input#donor-email").fill("grants@nordic-aid.org");

    await modal.locator("button:has-text('Add Supporter')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Donor "Nordic Humanitarian Agency" added successfully.');

    await expect(page.locator("table")).toContainText("Nordic Humanitarian Agency");
  });

  test("registers a grant agreement under the Grants tab", async ({ page }) => {
    await page.locator("button:has-text('Institutional Grants')").click();
    await expect(page.locator("table")).toContainText("Nutrition Emergency Response");

    // Open Register Grant modal
    await page.locator("button:has-text('+ Register Institutional Grant')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();

    await page.locator("select#grant-donor").selectOption("donor-1");
    await page.locator("input#grant-title").fill("Winterization Aid Window");
    await page.locator("input#grant-ref").fill("WAW-2026-01");
    await page.locator("input#grant-amount").fill("250000");
    await page.locator("input#grant-start").fill("2026-04-01");
    await page.locator("input#grant-end").fill("2026-10-31");

    await modal.locator("button:has-text('Register Grant')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Grant "Winterization Aid Window" registered successfully.');

    await expect(page.locator("table")).toContainText("Winterization Aid Window");
  });

  test("records incoming donation contribution under Donations tab", async ({ page }) => {
    await page.locator("button:has-text('Recorded Donations')").click();
    await expect(page.locator("table")).toContainText("WIRE-7782");

    // Open Record Contribution modal
    await page.locator("button:has-text('+ Record Incoming Contribution')").first().click();
    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();

    await page.locator("select#don-donor").selectOption("donor-1");
    await page.locator("input#don-amount").fill("75000");
    await page.locator("select#don-method").selectOption("bank_transfer");
    await page.locator("input#don-ref").fill("TRF-9901");

    await modal.locator("button:has-text('Record Contribution')").click();

    await expect(modal).not.toBeVisible();
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText("Donation contribution recorded successfully.");

    await expect(page.locator("table")).toContainText("TRF-9901");
  });
});

