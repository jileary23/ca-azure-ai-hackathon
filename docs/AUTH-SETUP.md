# Docs Site Authentication Setup

## Overview

The docs site is deployed to **Azure Static Web Apps (SWA)** with **invite-only** GitHub authentication.

- **Site URL:** https://ashy-hill-0c8e2040f.1.azurestaticapps.net
- **SWA Resource:** `cahack-docs` in resource group `rg-ca-hack`
- **Auth Provider:** GitHub (primary), Azure AD (backup)

Only users assigned the **`team`** role can view the site. Everyone else sees a 403 "Access Denied" page after authenticating. Unauthenticated visitors are redirected to GitHub login.

> **Note:** GitHub Pages has been replaced by Azure SWA for this site. The old GitHub Pages URL (`msftsean.github.io/ca-hackathon/`) should be disabled in the repo settings (Settings → Pages → disable).

---

## How to Invite a User

1. **Azure Portal** → navigate to Static Web App `cahack-docs` → **Role management**
2. Click **Invite** → select **GitHub** as the provider → enter the user's GitHub username
3. Assign the **`team`** role → send the invitation link to the user
4. The user clicks the link, authenticates with GitHub, and gains access

> Invitations can also be managed via the [Azure CLI](https://learn.microsoft.com/en-us/azure/static-web-apps/authentication-authorization#role-management):
> ```bash
> az staticwebapp users invite \
>   --name cahack-docs \
>   --resource-group rg-ca-hack \
>   --authentication-provider github \
>   --user-details "<github-username>" \
>   --role team \
>   --domain ashy-hill-0c8e2040f.1.azurestaticapps.net \
>   --invitation-expiration-in-hours 720
> ```

### Quick Invite for Jill (or anyone)

Replace `<github-username>` with the person's GitHub username:

```bash
az staticwebapp users invite \
  --name cahack-docs \
  --resource-group rg-ca-hack \
  --authentication-provider github \
  --user-details "<github-username>" \
  --role team \
  --domain ashy-hill-0c8e2040f.1.azurestaticapps.net \
  --invitation-expiration-in-hours 720
```

This generates an invitation link. Send it to the person — they click it, authenticate with GitHub, and get access.

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

## What the "team" Role Means

| Role | Who gets it | Access |
|------|-------------|--------|
| `anonymous` | Everyone (no login) | Auth login/logout pages only |
| `authenticated` | Any user who logs in | **Not used** — insufficient for site access |
| `team` | Explicitly invited users | Full docs site access |

The `team` role is a **custom role** — Azure SWA does not assign it automatically. Users must be invited through the Portal or CLI to receive it.

---

## Authentication Flow

```
User visits site
  → 401 (not logged in)
  → Redirect to /.auth/login/github
  → GitHub OAuth
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
