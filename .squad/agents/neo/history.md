# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### Docs Site Auth Hardening — GitHub + Invite-Only (2026-04-02)

**What changed:**
- `docs/staticwebapp.config.json`: Switched from AAD-only/open-authenticated to GitHub-primary/invite-only
- Removed 404 block on `/.auth/login/github`; made it primary auth (401 → GitHub redirect)
- AAD kept as backup provider (not blocked, just not the default redirect)
- Replaced `"authenticated"` role with custom `"team"` role on `/*` — only explicitly invited users can access
- Added 403 override → `/unauthorized.html` for users who authenticate but lack the `team` role
- Added security headers: `X-Permitted-Cross-Domain-Policies: none`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- Extended CSP `connect-src` to include `https://github.com` for OAuth redirects
- Created `docs/unauthorized.html` (friendly 403 page)
- Created `docs/AUTH-SETUP.md` (operator runbook for invitations and config)

**Architecture decisions:**
- Custom `team` role over `authenticated`: The built-in `authenticated` role is auto-assigned to anyone who logs in. Custom roles require explicit invitation via Azure Portal or CLI — this is the only way to enforce invite-only on SWA without a custom auth backend.
- GitHub as primary over AAD: GitHub usernames are the team's common identity. AAD remains usable but not the default entry point.
- 403 page as static HTML: Serves outside the SPA fallback to avoid requiring the full app bundle to load for denied users. Excluded from `navigationFallback` to prevent rewrite loops.
- Twitter remains blocked (404): No use case, reduces attack surface.
