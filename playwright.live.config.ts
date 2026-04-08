/**
 * Playwright config for live Azure Container App tests.
 * Extends base settings but removes the local webServer dependency.
 *
 * Run: npx playwright test --config playwright.live.config.ts
 */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "live-apps.spec.ts",
  timeout: 60_000,
  retries: 0,
  workers: 4,
  reporter: [["list"]],
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 30_000,
    navigationTimeout: 30_000,
  },
  // No webServer — tests hit live Azure URLs directly
});
