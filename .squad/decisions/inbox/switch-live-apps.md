# Decision: Live Apps Documentation Page

**Author:** Switch (Frontend Dev)
**Date:** 2026-04-07
**Status:** Proposed

## Context

Sean requested a docs page listing all live Azure Container App URLs for manual testing. The docs site has two distinct design systems: index.html (Outfit + DM Sans, fixed nav, landing page) and sub-pages (DM Serif Display + Source Sans 3, sticky nav, content pages).

## Decision

Built `docs/live-apps.html` following the **sub-page pattern** (architecture.html / getting-started.html), not the index.html landing page pattern.

### Rationale

- Live Apps is a content/reference page, not a marketing landing page
- Sub-page nav has cross-page links (Home, Architecture, Getting Started) — natural place to add Live Apps
- Index.html nav uses in-page anchor links (#accelerators, #architecture) — different navigation model
- Consistent user experience: all documentation sub-pages share the same shell

### Trade-offs

- The sub-page design is slightly less polished than index.html (simpler fonts, no card entrance animations beyond basic slideUp)
- Status dots are purely visual (gray/neutral) — no actual health check. This could be a future enhancement with a lightweight JS fetch to each `/health` endpoint.

## Impact

- 4 HTML files modified (index, architecture, getting-started + new live-apps)
- No build system changes — all static HTML with Tailwind CDN
- Navigation now has 4 items on sub-pages: Home, Architecture, Getting Started, Live Apps
