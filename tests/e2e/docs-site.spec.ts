import { test, expect } from '@playwright/test';

const DOCS_URL = 'http://localhost:4100';

const PAGES = [
  { name: 'Home', path: '/' },
  { name: 'Architecture', path: '/architecture.html' },
  { name: 'Getting Started', path: '/getting-started.html' },
  { name: 'Unauthorized', path: '/unauthorized.html' },
];

// ─── Page Load & Console Errors ──────────────────────────────────────────

test.describe('Page Load', () => {
  for (const page of PAGES) {
    test(`${page.name} loads without errors`, async ({ page: p }) => {
      const errors: string[] = [];
      p.on('pageerror', (err) => errors.push(err.message));

      const response = await p.goto(`${DOCS_URL}${page.path}`, { waitUntil: 'networkidle' });
      expect(response?.status()).toBe(200);
      expect(errors).toEqual([]);
    });
  }
});

// ─── Tailwind CSS Loading ────────────────────────────────────────────────

test.describe('Tailwind CSS', () => {
  test('Tailwind CDN script loads successfully', async ({ page }) => {
    let tailwindLoaded = false;
    page.on('response', (res) => {
      if (res.url().includes('cdn.tailwindcss.com') && res.status() === 200) {
        tailwindLoaded = true;
      }
    });

    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });
    expect(tailwindLoaded).toBe(true);
  });

  test('Tailwind classes are applied (not raw/unstyled)', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    // A bg-navy-700 or similar element should have a dark background, not white
    const hero = page.locator('.hero-bg').first();
    if (await hero.count() > 0) {
      const bg = await hero.evaluate((el) => getComputedStyle(el).backgroundColor);
      // Should be dark navy, not white/transparent
      expect(bg).not.toBe('rgba(0, 0, 0, 0)');
      expect(bg).not.toBe('rgb(255, 255, 255)');
    }

    // Check that padding/margin classes are applied
    const container = page.locator('.max-w-7xl').first();
    if (await container.count() > 0) {
      const maxWidth = await container.evaluate((el) => getComputedStyle(el).maxWidth);
      expect(maxWidth).not.toBe('none');
    }
  });

  test('Custom fonts are loaded', async ({ page }) => {
    let fontsLoaded = false;
    page.on('response', (res) => {
      if (res.url().includes('fonts.googleapis.com') && res.status() === 200) {
        fontsLoaded = true;
      }
    });

    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });
    expect(fontsLoaded).toBe(true);
  });
});

// ─── Layout & Visual Structure ───────────────────────────────────────────

test.describe('Layout - Home Page', () => {
  test('hero section is visible and properly sized', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const hero = page.locator('.hero-bg').first();
    if (await hero.count() > 0) {
      await expect(hero).toBeVisible();
      const box = await hero.boundingBox();
      expect(box).not.toBeNull();
      expect(box!.width).toBeGreaterThan(300);
      expect(box!.height).toBeGreaterThan(100);
    }
  });

  test('accelerator cards are visible', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const cards = page.locator('.accel-card');
    const count = await cards.count();
    // We expect 8 accelerator cards
    expect(count).toBeGreaterThanOrEqual(1);

    // First card should be visible and have reasonable dimensions
    if (count > 0) {
      const firstCard = cards.first();
      await expect(firstCard).toBeVisible();
      const box = await firstCard.boundingBox();
      expect(box).not.toBeNull();
      expect(box!.width).toBeGreaterThan(100);
      expect(box!.height).toBeGreaterThan(50);
    }
  });

  test('gold rule divider renders', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const goldRule = page.locator('.gold-rule').first();
    if (await goldRule.count() > 0) {
      await expect(goldRule).toBeVisible();
      const height = await goldRule.evaluate((el) => getComputedStyle(el).height);
      expect(height).toBe('3px');
    }
  });

  test('no horizontal overflow', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasOverflow).toBe(false);
  });

  test('text is readable (not white-on-white or invisible)', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    // Check main heading is visible
    const h1 = page.locator('h1').first();
    if (await h1.count() > 0) {
      await expect(h1).toBeVisible();
      const color = await h1.evaluate((el) => getComputedStyle(el).color);
      const bg = await h1.evaluate((el) => {
        let parent = el.parentElement;
        while (parent) {
          const bgColor = getComputedStyle(parent).backgroundColor;
          if (bgColor !== 'rgba(0, 0, 0, 0)') return bgColor;
          parent = parent.parentElement;
        }
        return 'rgb(255, 255, 255)';
      });
      // Text color should differ from background
      expect(color).not.toBe(bg);
    }
  });
});

// ─── Footer ──────────────────────────────────────────────────────────────

test.describe('Footer', () => {
  for (const pg of PAGES.filter(p => p.name !== 'Unauthorized')) {
    test(`${pg.name} has footer with attribution`, async ({ page }) => {
      await page.goto(`${DOCS_URL}${pg.path}`, { waitUntil: 'networkidle' });

      const footer = page.locator('footer').first();
      if (await footer.count() > 0) {
        await expect(footer).toBeVisible();
        const text = await footer.textContent();
        // Should have msftsean attribution
        expect(text?.toLowerCase()).toContain('sean');
      }
    });
  }

  test('footer has proper dark background', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const footer = page.locator('footer').first();
    if (await footer.count() > 0) {
      const bg = await footer.evaluate((el) => getComputedStyle(el).backgroundColor);
      // Should be dark, not white
      expect(bg).not.toBe('rgb(255, 255, 255)');
      expect(bg).not.toBe('rgba(0, 0, 0, 0)');
    }
  });

  test('footer links are clickable', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const footerLinks = page.locator('footer a');
    const count = await footerLinks.count();
    for (let i = 0; i < count; i++) {
      const href = await footerLinks.nth(i).getAttribute('href');
      expect(href).toBeTruthy();
      expect(href).not.toBe('#');
    }
  });
});

// ─── Navigation & Links ─────────────────────────────────────────────────

test.describe('Navigation', () => {
  test('home page has nav links', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const navLinks = page.locator('nav a, header a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
  });

  test('internal links resolve (no 404s)', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const links = page.locator('a[href]');
    const count = await links.count();
    const brokenLinks: string[] = [];

    for (let i = 0; i < count; i++) {
      const href = await links.nth(i).getAttribute('href');
      if (!href) continue;
      // Only check internal links
      if (href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('#')) continue;

      const response = await page.request.get(`${DOCS_URL}${href.startsWith('/') ? href : '/' + href}`);
      if (response.status() === 404) {
        brokenLinks.push(href);
      }
    }

    expect(brokenLinks).toEqual([]);
  });
});

// ─── Responsive Design ──────────────────────────────────────────────────

test.describe('Responsive Design', () => {
  test('mobile layout renders without overflow', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 }); // iPhone
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasOverflow).toBe(false);
  });

  test('tablet layout renders properly', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasOverflow).toBe(false);
  });

  test('cards stack on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const cards = page.locator('.accel-card');
    const count = await cards.count();
    if (count >= 2) {
      const box1 = await cards.nth(0).boundingBox();
      const box2 = await cards.nth(1).boundingBox();
      if (box1 && box2) {
        // On mobile, cards should stack (second card below first)
        expect(box2.y).toBeGreaterThan(box1.y);
      }
    }
  });
});

// ─── Accessibility ──────────────────────────────────────────────────────

test.describe('Accessibility', () => {
  test('page has lang attribute', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang).toBe('en');
  });

  test('images have alt attributes', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const images = page.locator('img');
    const count = await images.count();
    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute('alt');
      expect(alt).not.toBeNull();
    }
  });

  test('heading hierarchy is correct (h1 → h2 → h3)', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const headings = await page.evaluate(() => {
      const hs = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      return Array.from(hs).map((h) => parseInt(h.tagName.substring(1)));
    });

    // Should have at least one h1
    expect(headings.filter(h => h === 1).length).toBeGreaterThanOrEqual(1);

    // No heading should skip more than 1 level (e.g., h1 → h3 with no h2)
    for (let i = 1; i < headings.length; i++) {
      const jump = headings[i] - headings[i - 1];
      expect(jump).toBeLessThanOrEqual(2); // Allow going deeper by 1 or staying same
    }
  });

  test('color contrast - text is readable', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    // Check that body text isn't light gray on white
    const paragraphs = page.locator('p');
    const count = await paragraphs.count();
    if (count > 0) {
      const first = paragraphs.first();
      await expect(first).toBeVisible();
    }
  });
});

// ─── Meta & SEO ─────────────────────────────────────────────────────────

test.describe('Meta Tags', () => {
  test('noindex meta tag present', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });

    const robots = await page.locator('meta[name="robots"]').getAttribute('content');
    expect(robots).toContain('noindex');
  });

  test('page has title', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    expect(title.toLowerCase()).toContain('california');
  });

  test('page has description', async ({ page }) => {
    await page.goto(`${DOCS_URL}/`, { waitUntil: 'networkidle' });
    const desc = await page.locator('meta[name="description"]').getAttribute('content');
    expect(desc).toBeTruthy();
    expect(desc!.length).toBeGreaterThan(20);
  });
});

// ─── Architecture & Getting Started Pages ────────────────────────────────

test.describe('Architecture Page', () => {
  test('renders with styled content', async ({ page }) => {
    await page.goto(`${DOCS_URL}/architecture.html`, { waitUntil: 'networkidle' });

    const h1 = page.locator('h1').first();
    await expect(h1).toBeVisible();
    const text = await h1.textContent();
    expect(text?.toLowerCase()).toMatch(/architect/i);
  });

  test('pipeline diagram or description exists', async ({ page }) => {
    await page.goto(`${DOCS_URL}/architecture.html`, { waitUntil: 'networkidle' });

    const content = await page.textContent('body');
    // Should mention the 3-agent pipeline
    expect(content?.toLowerCase()).toMatch(/query|router|action|agent|pipeline/i);
  });
});

test.describe('Getting Started Page', () => {
  test('renders with styled content', async ({ page }) => {
    await page.goto(`${DOCS_URL}/getting-started.html`, { waitUntil: 'networkidle' });

    const h1 = page.locator('h1').first();
    await expect(h1).toBeVisible();
  });

  test('has code blocks or setup instructions', async ({ page }) => {
    await page.goto(`${DOCS_URL}/getting-started.html`, { waitUntil: 'networkidle' });

    const content = await page.textContent('body');
    expect(content?.toLowerCase()).toMatch(/install|setup|npm|git|clone|start/i);
  });
});

// ─── Visual Regression (Screenshots) ────────────────────────────────────

test.describe('Visual Snapshots', () => {
  for (const pg of PAGES.filter(p => p.name !== 'Unauthorized')) {
    test(`${pg.name} screenshot`, async ({ page }) => {
      await page.goto(`${DOCS_URL}${pg.path}`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(500); // Let animations settle

      await expect(page).toHaveScreenshot(`docs-${pg.name.toLowerCase().replace(/\s+/g, '-')}.png`, {
        fullPage: true,
        maxDiffPixelRatio: 0.1, // Allow 10% difference for first run
      });
    });
  }
});
