import { test, expect } from "@playwright/test";

const SITES = [
  { name: "Main Frontend", port: 4000, hasRobotsTxt: true },
  { name: "BenefitsCal Navigator (001)", port: 4005, hasRobotsTxt: true },
  { name: "Wildfire Response (002)", port: 4002, hasRobotsTxt: true },
  { name: "Medi-Cal Eligibility (003)", port: 4003, hasRobotsTxt: true },
  { name: "Permit Streamliner (004)", port: 4004, hasRobotsTxt: true },
  { name: "Knowledge Hub (006)", port: 4006, hasRobotsTxt: true },
  { name: "EDD Claims (007)", port: 4007, hasRobotsTxt: true },
  { name: "Emergency Chat (008)", port: 4008, hasRobotsTxt: true },
];

for (const site of SITES) {
  const url = `http://localhost:${site.port}`;

  test.describe(`${site.name} (port ${site.port})`, () => {
    // ── Page loads without JS errors ──
    test("page loads without console errors", async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (err) => errors.push(err.message));
      await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
      const critical = errors.filter(
        (e) =>
          !e.includes("fetch") &&
          !e.includes("ERR_CONNECTION_REFUSED") &&
          !e.includes("NetworkError") &&
          !e.includes("Failed to fetch")
      );
      expect(critical).toEqual([]);
    });

    // ── Footer is visible ──
    test("footer is visible and contains expected text", async ({ page }) => {
      await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
      const footer = page.locator('footer[role="contentinfo"]');
      await expect(footer).toBeVisible({ timeout: 5000 });

      const footerText = await footer.textContent();
      expect(footerText).toContain("Sean Gayle");
      expect(footerText).toMatch(/Microsoft Azure|Powered by/i);

      const link = footer.locator('a[href="https://github.com/msftsean"]');
      await expect(link).toBeVisible();
    });

    // ── Footer doesn't break layout ──
    test("footer is at bottom and does not overlap content", async ({ page }) => {
      await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
      const footer = page.locator('footer[role="contentinfo"]');
      await expect(footer).toBeVisible({ timeout: 5000 });

      const footerBox = await footer.boundingBox();
      expect(footerBox).not.toBeNull();
      expect(footerBox!.y).toBeGreaterThan(50);
      expect(footerBox!.height).toBeGreaterThan(20);
      expect(footerBox!.height).toBeLessThan(200);

      const viewport = page.viewportSize()!;
      expect(footerBox!.width).toBeLessThanOrEqual(viewport.width + 1);
    });

    // ── Page has noindex meta tag ──
    test("has noindex meta tag", async ({ page }) => {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });
      const robotsMeta = page.locator('meta[name="robots"]');
      await expect(robotsMeta).toHaveAttribute("content", /noindex/);
    });

    // ── robots.txt blocks all crawlers ──
    if (site.hasRobotsTxt) {
      test("robots.txt disallows all", async ({ request }) => {
        const resp = await request.get(`${url}/robots.txt`);
        expect(resp.status()).toBe(200);
        const body = await resp.text();
        expect(body).toContain("Disallow: /");
      });
    }

    // ── No JS bundle errors on load ──
    test("all JS bundles load successfully", async ({ page }) => {
      const failedResources: string[] = [];
      page.on("requestfailed", (req) => {
        if (req.resourceType() === "script") {
          failedResources.push(req.url());
        }
      });
      await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
      expect(failedResources).toEqual([]);
    });

    // ── Accessibility: footer has contentinfo role ──
    test("footer has contentinfo landmark role", async ({ page }) => {
      await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
      const footer = page.locator('[role="contentinfo"]');
      await expect(footer).toBeVisible();
    });

    // ── Visual snapshot ──
    test("visual snapshot", async ({ page }) => {
      await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(500);
      await page.screenshot({
        path: `tests/e2e/screenshots/${site.name.replace(/[^a-zA-Z0-9]/g, "-")}.png`,
        fullPage: true,
      });
    });
  });
}
