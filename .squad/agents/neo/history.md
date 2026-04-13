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

### Per-Accelerator Red Team Configs + Input Validation Middleware (2026-04-03)

**What changed:**
- Created `accelerators/*/backend/evals/red_team_config.json` for all 8 accelerators (80 total adversarial scenarios)
- Created `shared/security/input_validator.py` — shared input validation middleware for LLM input sanitization
- Created `shared/security/__init__.py` and `shared/security/README.md`

**Red team coverage per accelerator:**
- 001 (BenefitsCal): Benefits fraud, FPL manipulation, PII exfiltration (10 scenarios)
- 002 (Wildfire): False reports, resource diversion, ops data extraction (10 scenarios)
- 003 (Medi-Cal): Document fraud, MAGI gaming, patient data leaks (10 scenarios)
- 004 (Permits): Fake permits, SLA manipulation, fee evasion, inspection bypass (10 scenarios)
- 005 (Procurement): Forged attestations, NIST score gaming, review bypass (10 scenarios)
- 006 (Knowledge Hub): Privilege escalation, cross-agency data leaks, impersonation (10 scenarios)
- 007 (EDD): Identity theft, claim fraud, verification bypass (10 scenarios)
- 008 (Multilingual): False alerts, location manipulation, multilingual injection (10 scenarios)

**Input validator capabilities:**
- Max input length enforcement (default 2000 chars)
- 5 prompt injection pattern categories (role override, instruction override, system directives, output manipulation, delimiter injection)
- PII detection: SSN, email, phone, credit card, CA driver's license
- HTML/script tag stripping with dangerous element detection
- Unicode NFKC normalization + zero-width character removal

**Architecture decision:** Input validator flags PII but does not block — blocking PII would prevent legitimate benefit/claim inquiries that naturally include personal information. Prompt injection and overlength inputs are the only hard blocks.
