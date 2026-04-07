# Decision: GitHub Auth + Invite-Only for Docs Site

**Timestamp:** 2026-04-02  
**Authority:** Neo (Security) — requested by msftsean  
**Status:** ✅ Implemented

## Context

The docs site (`docs/staticwebapp.config.json`) was configured with AAD-only authentication and the built-in `authenticated` role, meaning **any Microsoft account holder** could access the site. GitHub login was explicitly blocked (404). No invitation or role-gating mechanism was in place.

## Threat Assessment

- **Over-permissive access:** `authenticated` role auto-grants to any login — no way to restrict to team members
- **Wrong identity provider:** Team uses GitHub identities, but GitHub auth was blocked
- **No deny page:** Users who shouldn't have access had no feedback mechanism

## Decision

1. **GitHub as primary auth** — 401 redirects to `/.auth/login/github`
2. **AAD as backup** — still accessible at `/.auth/login/aad`, not blocked
3. **Twitter blocked** — returns 404 (no use case)
4. **Custom `team` role** — replaces `authenticated` on all content routes. Requires explicit invitation via Azure Portal or CLI.
5. **403 handling** — authenticated users without `team` role see `/unauthorized.html` explaining they need an invitation
6. **Security headers hardened** — added `X-Permitted-Cross-Domain-Policies`, `Permissions-Policy`, extended CSP for GitHub OAuth

## Affected Files

- `docs/staticwebapp.config.json` — routing, auth, headers
- `docs/unauthorized.html` — 403 page (new)
- `docs/AUTH-SETUP.md` — operator runbook (new)

## Implications

- **For Sean:** Invite users via Azure Portal → Static Web App → Role management → assign `team` role
- **For Switch:** No frontend code changes needed — SWA handles auth at the edge
- **For deployment:** Config deploys with the static site; no infra changes required
- **Rollback:** Change 401 redirect back to `/.auth/login/aad` and replace `team` with `authenticated` on `/*` route

## Risks

- If Azure Portal role management is unavailable, CLI fallback exists (`az staticwebapp users invite`)
- Users with both GitHub and AAD accounts: role assignment is per-provider. Invite must match the provider they authenticate with.
