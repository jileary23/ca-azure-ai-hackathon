# Docs Site Authentication Setup

## Overview

The docs site is deployed to **Azure Static Web Apps (SWA)** with **invite-only** GitHub authentication.

- **Site URL:** https://ashy-hill-0c8e2040f.1.azurestaticapps.net
- **SWA Resource:** `cahack-docs` in resource group `rg-ca-hack`
- **Auth Provider:** GitHub (primary), Azure AD (backup)

Any user who authenticates with GitHub can access the site. To restrict to invite-only, change `"authenticated"` to `"team"` in `staticwebapp.config.json` and manage invitations via Azure Portal.

> **Note:** GitHub Pages has NO authentication support — it's always public. To secure the docs, we use Azure SWA instead. You should **disable GitHub Pages** in repo settings (Settings → Pages → disable) to avoid having an unauthenticated copy at `msftsean.github.io/ca-hackathon/`.

---

## Access Levels

### Current: GitHub-authenticated (open to any GitHub user)

The site currently requires GitHub login but does **not** restrict to specific users. Any GitHub user can access after authenticating.

### To switch to invite-only:

1. Edit `docs/staticwebapp.config.json` — change `"authenticated"` to `"team"` in the `/*` route
2. Redeploy (see Deploying Updates below)
3. Invite users via Azure Portal → Static Web App `cahack-docs` → **Role management** → Invite

| Role | Who gets it | Access |
|------|-------------|--------|
| `anonymous` | Everyone (no login) | Auth login/logout pages only |
| `authenticated` | Any GitHub user who logs in | **Current setting** — full site access |
| `team` | Explicitly invited users only | Invite-only (tighter security) |

### Deploying Updates

From the codespace, deploy docs changes directly:

```bash
SWA_TOKEN=$(curl -s -X POST \
  -H "Authorization: Bearer $(azd auth token)" \
  -H "Content-Type: application/json" \
  "https://management.azure.com/subscriptions/b1ade9aa-a8a5-454e-9531-3f8ba1b1a06a/resourceGroups/rg-ca-hack/providers/Microsoft.Web/staticSites/cahack-docs/listSecrets?api-version=2022-09-01" \
  -d '{}' | python3 -c "import json,sys; print(json.load(sys.stdin)['properties']['apiKey'])")

swa deploy docs/ --deployment-token "$SWA_TOKEN" --env production
```

---

## Authentication Flow

```
User visits site
  → 302 redirect to /.auth/login/github
  → GitHub OAuth login
  → Access granted (any authenticated GitHub user)
```

To enable invite-only flow (after switching to `team` role):
```
User visits site
  → 302 redirect to /.auth/login/github
  → GitHub OAuth login
  → If user has "team" role → access granted
  → If user lacks "team" role → 403 → /unauthorized.html
```

---

## Switching Back to Azure AD (if needed)

Edit `docs/staticwebapp.config.json` and change the 401 redirect:

```json
"responseOverrides": {
  "401": { "redirect": "/.auth/login/aad", "statusCode": 302 }
}
```

No other changes are needed — AAD login is already enabled as a backup provider.

---

## Security Headers

The config enforces these headers on all responses:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Blocks clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Legacy XSS filter |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer leakage |
| `X-Permitted-Cross-Domain-Policies` | `none` | Blocks Flash/PDF cross-domain |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disables device APIs |
| `Content-Security-Policy` | `default-src 'self'; ...` | Restricts resource loading |

---

## Files

| File | Purpose |
|------|---------|
| `docs/staticwebapp.config.json` | SWA routing, auth, headers |
| `docs/unauthorized.html` | 403 page for non-invited users |
| `docs/AUTH-SETUP.md` | This file |
