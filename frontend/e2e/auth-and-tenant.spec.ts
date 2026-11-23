import { test, expect } from "@playwright/test";
import { setupMockApi } from "./fixtures";

test.describe("Authentication and Multi-Tenant Boundaries", () => {
  test("unauthenticated visitor is redirected to login", async ({ page }) => {
    await setupMockApi(page, { authenticated: false });

    await page.goto("/");
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator(".brand-title")).toHaveText("Abren One");
    await expect(page.locator("button.login-btn")).toBeVisible();
  });

  test("login form validates required fields inline", async ({ page }) => {
    await setupMockApi(page, { authenticated: false });

    await page.goto("/login");
    await page.locator("button.login-btn").click();

    await expect(page.locator("#username-error")).toHaveText("Username is required.");
    await expect(page.locator("#password-error")).toHaveText("Password is required.");
    await expect(page).toHaveURL(/.*\/login/);
  });

  test("user can log in, see dashboard, and receive welcome toast", async ({ page }) => {
    await setupMockApi(page, { authenticated: false });

    await page.goto("/login");
    await page.locator("input#username").fill("admin");
    await page.locator("input#password").fill("password123");

    // Enable authenticated response for post-login calls
    await setupMockApi(page, { authenticated: true });

    await page.locator("button.login-btn").click();

    // Verify redirection to dashboard
    await expect(page).toHaveURL("http://localhost:5173/");
    await expect(page.locator(".page-title")).toHaveText("Operations Overview");

    // Verify toast notification appeared
    const toast = page.locator(".toast--success");
    await expect(toast).toBeVisible();
    await expect(toast).toContainText("Signed in as admin");
  });

  test("authenticated user can switch and provision organizations", async ({ page }) => {
    await setupMockApi(page, { authenticated: true });

    await page.goto("/");
    await expect(page.locator(".page-title")).toHaveText("Operations Overview");

    // Verify current tenant in header
    const orgSelect = page.locator("select#org-select");
    await expect(orgSelect).toBeVisible();
    await expect(orgSelect).toContainText("Abren Relief Initiative");

    // Open provision modal
    await orgSelect.selectOption("__NEW__");

    const modal = page.locator("dialog[open]");
    await expect(modal).toBeVisible();
    await expect(modal).toContainText("Provision New Organization");

    // Fill form and provision
    await page.locator("input#org-name").fill("Horn of Africa Nutrition Mission");
    await page.locator("input#org-slug").fill("horn-africa-nutrition");
    await modal.locator("button.btn-primary").click();

    // Verify modal closed and success toast appeared
    await expect(modal).not.toBeVisible();
  });

  test("user can log out successfully", async ({ page }) => {
    await setupMockApi(page, { authenticated: true });

    await page.goto("/");
    await page.locator("button:has-text('Log Out')").click();

    await expect(page).toHaveURL(/.*\/login/);
  });
});
