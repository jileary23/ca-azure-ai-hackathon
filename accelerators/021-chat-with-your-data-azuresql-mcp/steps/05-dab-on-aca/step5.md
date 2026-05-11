# Step 5 — Host Data API Builder on Azure Container Apps

[← back to step 4](../04-dab-local/step4.md) · [up to root README](../../README.md) · [step 6 → Calling hosted DAB](../06-calling-hosted-dab/README.md)

> **You are here:** step 4 ran DAB on `http://localhost:5000` as
> *you*. Step 5 takes the same image and the same `dab-config.json`
> structure, drops them into **Azure Container Apps**, and connects
> to Azure SQL as the **step 1 User-Assigned Managed Identity** —
> not your developer login. After this step DAB has a public HTTPS
> FQDN with no SQL passwords anywhere.

---

## What you'll build

```text
              ┌────────────────────────────────────┐
              │  Azure Container Apps environment  │
              │   (managed env + Log Analytics)    │
              │                                    │
   public ───►│   ┌──────────────────────────┐     │
   HTTPS      │   │   Container App: dab     │     │
              │   │   image: ACR/dab:latest  │     │
              │   │   identity: step-1 UAMI  │     │
              │   └─────────────┬────────────┘     │
              └─────────────────┼──────────────────┘
                                │ tcp 1433
                                │ Authentication=Active Directory
                                │ Managed Identity;User Id=<UAMI clientId>
                                ▼
                       ┌──────────────────┐
                       │   Azure SQL DB   │
                       │   (from step 1)  │
                       └──────────────────┘
```

What the Bicep + script set up:

| Resource | Why |
|---|---|
| **Azure Container Registry** (Basic, admin disabled) | Holds the DAB image. Created by the script (not Bicep) so the image can exist before the app tries to pull it. |
| **AcrPull** role on the registry | Granted to the step 1 UAMI so ACA can pull without admin creds. |
| **Log Analytics workspace** | Backing store for ACA stdout/stderr. |
| **Container Apps managed environment** | Lives in your subscription's network. |
| **Container App `dab`** | Runs the image, attaches the UAMI, exposes port 5000 over public HTTPS, mounts `SQL_CONNECTION_STRING` from a secret. |

No new SQL is created — step 2's `01-create-uami-db-user.sql`
already mapped this same UAMI to a DB user with the right grants.

---

## Prerequisites

- Steps 1, 2, 3 completed (you have `outputs.json` and the SP).
- Step 4 verified locally (optional but recommended — same config).
- Azure CLI ≥ 2.60 with the `containerapp` extension. The script
  installs it for you if missing.
- The deploying identity has **Owner** or
  **Contributor + User Access Administrator** on the resource group
  (the script creates a role assignment).

You do **not** need Docker installed locally. The script uses
[ACR Tasks][acr-tasks] (`az acr build`) to build the image inside Azure.

[acr-tasks]: https://learn.microsoft.com/azure/container-registry/container-registry-tasks-overview

---

## What's in this folder

```text
steps/05-dab-on-aca/
├── step5.md                  ← you are reading this
├── deploy.ps1                ← orchestrates ACR create, image build, Bicep deploy
├── bicep/main.bicep          ← LAW + ACA env + ACA app + AcrPull role
├── docker/
│   ├── Dockerfile            ← FROM mcr.../data-api-builder + COPY dab-config.json
│   └── dab-config.json       ← same shape as step 4, but connection-string = @env(...)
└── byo/README.md             ← adding your own table / SP for the hosted build
```

The hosted `dab-config.json` differs from the step 4 one in three places:

1. `connection-string` is `@env('SQL_CONNECTION_STRING')` — set by ACA, not baked in.
2. `host.mode` is `production` (terse errors, no Banana Cake Pop).
3. `cors.origins` is `["*"]` for tutorial convenience (lock it down for real workloads).

Permissions still default to `anonymous`. **For real workloads**, switch every
entity to `authenticated` and put Entra ID auth in front — see the
"Locking it down" section at the bottom of this page.

---

## Run it

From the repo root:

```powershell
.\steps\05-dab-on-aca\deploy.ps1
```

That runs six numbered sections — you should see something like:

```text
1/6  Loading step 1 outputs
2/6  Verifying az + containerapp extension
3/6  Ensuring Azure Container Registry exists
4/6  Building image via ACR Tasks: sqlragacrdevz4gsb7.azurecr.io/dab:latest
5/6  Building SQL connection string
6/6  Deploying ACA infrastructure
Done

DAB is live at: https://sqlrag-dab-dev.<random>.<region>.azurecontainerapps.io
```

The Bicep waits for the AcrPull role to be in place before creating
the container app, but role-assignment propagation occasionally lags
by a minute — if the first revision fails with `ImagePullBackOff`,
wait a moment and the ACA control plane will retry automatically.

The script also writes `steps/05-dab-on-aca/outputs.json` with the
registry name, image tag, and FQDN — step 6 reads it.

---

## Verify

Grab the FQDN from `outputs.json`:

```powershell
$dab = (Get-Content .\steps\05-dab-on-aca\outputs.json | ConvertFrom-Json).acaAppUrl
"DAB URL: $dab"
```

### REST — list products

```powershell
curl "$dab/api/Product" | ConvertFrom-Json | Select-Object -First 3
```

### REST — call the hybrid search SP

```powershell
$body = @{
  queryText = 'lightweight running shoes that handle rain'
  top       = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri    "$dab/api/FindSimilarReviewsHybrid" `
  -ContentType 'application/json' `
  -Body   $body |
  Select-Object -ExpandProperty value |
  Format-Table ProductName, Rating, rrf_score, ReviewText -AutoSize
```

### MCP `tools/list`

Same Streamable-HTTP handshake as step 4 — just point at the public
FQDN's `/mcp` path:

```powershell
$mcp    = "$dab/mcp"
$accept = 'application/json, text/event-stream'

function Read-McpSse([string]$content) {
  ($content -split "`n" |
    Where-Object { $_ -like 'data:*' } |
    ForEach-Object { $_.Substring(5).Trim() }) -join "`n" | ConvertFrom-Json
}

$initBody = @{
  jsonrpc='2.0'; id=1; method='initialize'
  params=@{
    protocolVersion='2025-03-26'
    capabilities=@{}
    clientInfo=@{ name='pwsh'; version='1.0' }
  }
} | ConvertTo-Json -Depth 6

$resp      = Invoke-WebRequest -Method Post -Uri $mcp `
              -ContentType 'application/json' `
              -Headers @{ Accept = $accept } -Body $initBody
$sessionId = [string]$resp.Headers['Mcp-Session-Id'][0]
$headers   = @{ Accept = $accept; 'Mcp-Session-Id' = $sessionId }

Invoke-WebRequest -Method Post -Uri $mcp -ContentType 'application/json' -Headers $headers `
  -Body (@{ jsonrpc='2.0'; method='notifications/initialized' } | ConvertTo-Json) | Out-Null

$listResp = Invoke-WebRequest -Method Post -Uri $mcp -ContentType 'application/json' -Headers $headers `
  -Body (@{ jsonrpc='2.0'; id=2; method='tools/list' } | ConvertTo-Json)

(Read-McpSse $listResp.Content).result.tools | Format-Table name, description -Wrap
```

### Tail logs

```powershell
$rg  = (Get-Content .\steps\01-foundation\outputs.json | ConvertFrom-Json).resourceGroup
$app = (Get-Content .\steps\05-dab-on-aca\outputs.json | ConvertFrom-Json).acaAppName
az containerapp logs show -g $rg -n $app --follow
```

---

## How auth works in production

Inside the container:

- The ACA platform mounts an IMDS endpoint that hands out tokens for
  any UAMI attached to the app. We attached one — the step 1 UAMI.
- `AZURE_CLIENT_ID` is set on the container so any `DefaultAzureCredential`-
  based code picks **that** UAMI (not the system-assigned one, which
  doesn't exist here, but explicit is safer).
- The connection string says
  `Authentication=Active Directory Managed Identity;User Id=<UAMI clientId>`.
  `Microsoft.Data.SqlClient` (which DAB uses under the covers)
  recognizes that, fetches a SQL access token from IMDS for that
  client id, and presents it to Azure SQL.
- Azure SQL maps the token's `oid` claim to the database user that
  step 2 created (`CREATE USER [sqlrag-uami-dev] FROM EXTERNAL PROVIDER`)
  and grants its role memberships (`db_datareader`, `db_datawriter`,
  `EXECUTE ON SCHEMA::dbo`).

No SQL password ever exists anywhere. The ACR pull works the same
way — ACA's identity broker presents an AAD token for the same UAMI,
ACR checks for the AcrPull role assignment, and serves the manifest.

---

## Locking it down (recommended before real use)

The tutorial defaults are open so you can demo end-to-end fast. Before
fronting real users:

1. **Switch entity permissions** from `anonymous` to `authenticated`
   in `docker/dab-config.json`, rebuild, redeploy.
2. **Configure DAB authentication** — add a
   `runtime.host.authentication` block pointing at Entra ID and
   require valid Bearer tokens.
3. **Lock CORS** — replace `"*"` with your actual front-end origins.
4. **Restrict ACA ingress** — set `ipSecurityRestrictions` on the
   ingress to your VNet / known egress IPs.

Step 6 demos calling DAB with anonymous access; step 8 (optional)
shows a Foundry agent calling MCP. When you adopt token-based auth,
both call patterns gain an `Authorization: Bearer …` header — nothing
else changes.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `deploy.ps1` fails at "Ensuring resource providers" | Subscription policy blocks `register` | Have an owner register `Microsoft.App`, `Microsoft.ContainerRegistry`, `Microsoft.OperationalInsights` once for the subscription |
| `az acr build` fails with `Run failed`: paste the inner error | Usually a Dockerfile typo or upstream image pull throttle | `az acr task logs -r <acrName> --run-id <runId>` shows full output |
| ACA app stuck in `ImagePullBackOff` | AcrPull role hasn't propagated yet | Wait ~60 s; ACA retries. If it persists, run `az role assignment list --assignee <uamiPrincipalId> --all` and confirm `AcrPull` is there |
| ACA logs show `Login failed for token-identified principal` | UAMI hasn't been mapped to a DB user | Re-run `steps/02-embeddings-in-sql/sql/01-create-uami-db-user.sql` against `ProductsDB` |
| ACA logs show `You do not have permission to run 'sys.sp_invoke_external_rest_endpoint'` | UAMI lacks `EXECUTE ANY EXTERNAL ENDPOINT` (works locally because your dev account is admin) | Re-run `01-create-uami-db-user.sql` (current version grants this), or one-off: `GRANT EXECUTE ANY EXTERNAL ENDPOINT TO [<uamiName>];` |
| ACA logs show `Cannot find the credential '<endpoint>', because it does not exist or you do not have permission` | UAMI doesn't have `REFERENCES` on the database-scoped credential created in step 2 | Re-run `02-create-credential.sql` (current version grants it), or one-off: `GRANT REFERENCES ON DATABASE SCOPED CREDENTIAL::[<endpoint-no-trailing-slash>] TO [<uamiName>];` |
| `Invoke-RestMethod` fails with `Cannot follow an insecure redirection` on the SP POST | DAB returned a 301 with an `http://` Location because Kestrel didn't honor `X-Forwarded-Proto` from the ACA edge | Set `ASPNETCORE_FORWARDEDHEADERS_ENABLED=true` on the container (already in `bicep/main.bicep`); redeploy with `.\steps\05-dab-on-aca\deploy.ps1 -SkipBuild` |
| REST returns 500 with `Cannot find the credential '...openai.azure.com/'` (note the trailing slash) | Old `get_embedding` SP still installed (trailing-slash bug) | Re-apply `steps/02-embeddings-in-sql/sql/03-create-get-embedding-sp.sql` — fixed version normalizes the endpoint |
| HTTP 404 on `/api/Product` | DAB couldn't load `dab-config.json` and is serving its fallback page | `az containerapp logs show -g <rg> -n <app>` — usually a JSON schema error in the config |
| MCP `tools/list` returns the "Not Acceptable" or "session" errors from step 4 | Same Streamable-HTTP gotchas | See step 4's [troubleshooting table](../04-dab-local/step4.md#troubleshooting) |

---

## What's next

→ [Step 6 — Calling hosted DAB](../06-calling-hosted-dab/README.md):
fully worked REST + MCP examples against the URL you just deployed,
plus how those calls plug into a Foundry agent in step 8.

---

## Bring your own table

If you ran the BYO appendices in [step 2](../02-embeddings-in-sql/byo/README.md)
and [step 3](../03-hybrid-search-sp/byo/README.md), see
[byo/README.md](./byo/README.md) for adding your own entity + SP to
the hosted image.
