# Step 4 — Run Data API Builder locally

[← back to step 3](../03-hybrid-search-sp/step3.md) · [up to root README](../../README.md) · [step 5 → DAB on ACA](../05-dab-on-aca/README.md)

> **You are here:** you have a working Azure SQL database with vector
> embeddings and a `dbo.find_similar_reviews_hybrid` stored procedure.
> Now you'll point [Data API Builder][dab] at it and get REST,
> GraphQL, **and MCP** endpoints on `http://localhost:5000` —
> entirely on your laptop, no new Azure resources.

[dab]: https://learn.microsoft.com/azure/data-api-builder/

---

## What you'll build

```text
┌─────────────────────┐    ┌────────────────────────────┐
│  Your laptop        │    │  Azure SQL (from step 1)   │
│                     │    │                            │
│  dab start          │───▶│  dbo.Products              │
│   ├─ REST  /api     │    │  dbo.ProductReviews        │
│   ├─ GQL   /graphql │    │  dbo.find_similar_         │
│   └─ MCP   /mcp     │    │      reviews_hybrid (SP)   │
└─────────────────────┘    └────────────────────────────┘
       ▲
       │  Authentication=Active Directory Default
       │  → uses YOUR identity from `az login`
```

| Endpoint | URL | What it gives you |
|---|---|---|
| REST | `http://localhost:5000/api/Product` | CRUD-style routes for each table |
| REST (SP) | `POST http://localhost:5000/api/FindSimilarReviewsHybrid` | Calls the hybrid search SP |
| GraphQL | `http://localhost:5000/graphql` | Single schema across all entities |
| MCP | `http://localhost:5000/mcp` | `tools/list` + `tools/call` for AI agents |

Production with the **managed identity** comes in
[step 5](../05-dab-on-aca/README.md); locally we use *your* developer
identity because (a) it's already a SQL AAD admin from step 1, and
(b) UAMIs can't be `az login`'d from a laptop anyway.

---

## Prerequisites

From the root README ([prereq section F](../../README.md)):

- .NET 8 SDK
- DAB CLI: `dotnet tool install --global Microsoft.DataApiBuilder`
- `az login` to the tenant/subscription that owns the SQL server

Verify:

```powershell
dotnet --version    # 8.x+
dab --version       # 1.7+ (MCP requires 1.7)
az account show     # confirm right tenant
```

> **Note on DAB versions:** MCP is GA in 1.7. *Custom* MCP tools for
> stored procedures (`mcp.custom-tool: true`) are 2.0-preview. This
> lesson uses the default behavior, which already exposes the SP as
> a standard execute tool through DAB's DML tool surface.

---

## What's in this folder

```text
steps/04-dab-local/
├── step4.md                    ← you are reading this
├── deploy.ps1                  ← generates dab-config.json from outputs.json
├── dab-config.template.json    ← config skeleton with <<SQL_FQDN>> placeholders
└── byo/README.md               ← adding your own table / SP
```

`dab-config.json` itself is **generated** by `deploy.ps1` — it lives
in this folder at runtime but is excluded from git by the repo-root
[`.gitignore`](../../.gitignore) so your SQL server FQDN never gets
committed.

---

## Run it

### 1. Generate `dab-config.json`

From the **repo root**:

```powershell
.\steps\04-dab-local\deploy.ps1
```

This:

1. reads `steps/01-foundation/outputs.json` for the SQL FQDN + DB name,
2. confirms `dotnet`, `dab`, and `az` are present and you're logged in,
3. substitutes `<<SQL_FQDN>>` / `<<SQL_DB>>` in the template,
4. writes `steps/04-dab-local/dab-config.json`.

### 2. Start DAB

`dab start` is a long-running server, so run it yourself:

```powershell
cd .\steps\04-dab-local
dab start
```

You should see:

```text
Now listening on: http://localhost:5000
Successfully completed runtime initialization.
```

Leave that window running. Open a *second* terminal for the calls below.

> **Tip:** if you'd rather have `deploy.ps1` launch it for you, add
> `-LaunchDab`. Ctrl-C still stops it.

---

## Verify

### REST — list products

```powershell
curl http://localhost:5000/api/Product | ConvertFrom-Json | Select-Object -First 3
```

Returns a `value` array of products.

### REST — call the hybrid search SP

```powershell
$body = @{
  queryText = 'lightweight running shoes that handle rain'
  top       = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri    http://localhost:5000/api/FindSimilarReviewsHybrid `
  -ContentType 'application/json' `
  -Body   $body |
  Select-Object -ExpandProperty value |
  Format-Table ProductName, Rating, rrf_score, ReviewText -AutoSize
```

> **Why only `queryText` and `top`?** You completed the [required
> step 3 upgrade](../03-hybrid-search-sp/upgrade-external-model/README.md)
> before getting here, so the SP no longer takes the OpenAI endpoint or
> deployment name as parameters — they're baked into the registered
> `EXTERNAL MODEL EmbeddingModel`.

You should see the same top-5 ranking you got from step 3's smoke
test, only now coming back through HTTP.

### GraphQL

Browse to `http://localhost:5000/graphql` in your browser — the
Banana Cake Pop UI lets you run:

```graphql
query {
  products(first: 3) {
    items { ProductID Name Category }
  }
}
```

### MCP `tools/list`

DAB's MCP endpoint speaks the [Streamable HTTP transport][mcp-http],
which is JSON-RPC tunneled over Server-Sent Events. A raw
`tools/list` call **will not work**. The protocol requires:

1. `POST initialize` — the server returns a session id in the
   `Mcp-Session-Id` response header. The response body is SSE
   (`event: message\ndata: {...json...}`), not plain JSON.
2. `POST notifications/initialized` — handshake confirmation
   (returns 202 with no body).
3. Any further requests (`tools/list`, `tools/call`, …) must carry
   that `Mcp-Session-Id` header *and* an `Accept` header that lists
   **both** `application/json` and `text/event-stream`. Their
   response bodies are also SSE — pull the JSON out of the `data:`
   line.

Two PowerShell footguns to watch for:

- `Invoke-WebRequest` returns header values as **string arrays**, so
  use `$resp.Headers['Mcp-Session-Id'][0]`. Passing the raw array
  into a later request's `-Headers` hashtable produces `Session not
  found`.
- `Invoke-RestMethod` can't auto-parse SSE bodies; use
  `Invoke-WebRequest` + a tiny SSE parser as below.

[mcp-http]: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http

```powershell
$mcp    = 'http://localhost:5000/mcp'
$accept = 'application/json, text/event-stream'

function Read-McpSse([string]$content) {
  ($content -split "`n" |
    Where-Object { $_ -like 'data:*' } |
    ForEach-Object { $_.Substring(5).Trim() }) -join "`n" | ConvertFrom-Json
}

# 1. initialize → capture session id from response header
$initBody = @{
  jsonrpc = '2.0'; id = 1; method = 'initialize'
  params  = @{
    protocolVersion = '2025-03-26'
    capabilities    = @{}
    clientInfo      = @{ name = 'pwsh'; version = '1.0' }
  }
} | ConvertTo-Json -Depth 6

$resp      = Invoke-WebRequest -Method Post -Uri $mcp `
              -ContentType 'application/json' `
              -Headers @{ Accept = $accept } -Body $initBody
$sessionId = [string]$resp.Headers['Mcp-Session-Id'][0]
"Session: $sessionId"

$headers = @{ Accept = $accept; 'Mcp-Session-Id' = $sessionId }

# 2. send required 'initialized' notification
Invoke-WebRequest -Method Post -Uri $mcp `
  -ContentType 'application/json' -Headers $headers `
  -Body (@{ jsonrpc = '2.0'; method = 'notifications/initialized' } | ConvertTo-Json) |
  Out-Null

# 3. tools/list — body is SSE, so parse it
$listResp = Invoke-WebRequest -Method Post -Uri $mcp `
  -ContentType 'application/json' -Headers $headers `
  -Body (@{ jsonrpc = '2.0'; id = 2; method = 'tools/list' } | ConvertTo-Json)

(Read-McpSse $listResp.Content).result.tools | Format-Table name, description -Wrap
```

You should see DAB's DML tools (`describe_entities`, `read_records`,
`execute_entity`, …) listed. The `execute_entity` tool can invoke
`FindSimilarReviewsHybrid`.

---

## How auth works locally

Look at the generated `dab-config.json`:

```json
"connection-string": "Server=tcp:...,1433;Database=ProductsDB;Authentication=Active Directory Default;Encrypt=True;..."
```

`Active Directory Default` walks the standard `DefaultAzureCredential`
chain (env vars → Managed Identity → `az` CLI → VS / VS Code → …).
On a developer laptop the `az login` token wins, so DAB connects to
SQL **as you**. That means:

- You don't need a SQL password anywhere.
- You don't need to add a DB user for DAB — you're already the AAD
  admin from step 1, so you can read every table.
- This is **local-only**. In step 5 the container in ACA will use the
  step 1 UAMI instead (same connection string, same code, different
  credential at the bottom of the chain).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `dab: command not found` | DAB CLI not on PATH | `dotnet tool install --global Microsoft.DataApiBuilder`, then open a new terminal |
| `Login failed for user '<token-identified principal>'` | Wrong tenant in `az login` | `az login --tenant <tenant-id>` for the tenant that owns the SQL server |
| `Cannot open server '...' requested by the login. Client with IP address '...' is not allowed` | Your IP isn't in the SQL server firewall | Add a firewall rule for your IP, or re-run step 1 — its Bicep already allows Azure services and you can extend it with your client IP |
| `dab start` exits immediately with a JSON parse error | `dab-config.json` not regenerated after editing template | Re-run `deploy.ps1`, or fix the JSON |
| Port 5000 already in use | Something else is listening | `dab start --port 5050` |
| REST returns 401 / 403 | You set entity permissions to `authenticated` but called anonymously | The shipped config uses `anonymous` everywhere for local dev — leave it that way until step 5 |
| SP call returns empty `value` | Embeddings missing on the underlying rows, or the EXTERNAL MODEL isn't reachable | Re-run the step 2 backfill, then re-run the [step 3 upgrade](../03-hybrid-search-sp/upgrade-external-model/README.md) smoke test against the EXTERNAL MODEL |
| `DatabaseOperationFailed` / `Cannot find the credential '...openai.azure.com/'` | Older copy of `dbo.get_embedding` passed the endpoint through with a trailing `/`, mismatching the credential name | Re-apply `steps/02-embeddings-in-sql/sql/03-create-get-embedding-sp.sql` — the current version strips trailing slashes internally |
| `No connection could be made because the target machine actively refused it` on `localhost:5000` | `dab start` isn't running (or crashed) | Restart it: `cd .\steps\04-dab-local; dab start` |
| MCP call returns `-32000 Not Acceptable: Client must accept both application/json and text/event-stream` | Streamable HTTP transport requires both `Accept` types | Add `-Headers @{ Accept = 'application/json, text/event-stream' }` (or `curl -H "Accept: application/json, text/event-stream"`) |
| MCP call returns `Bad Request: A new session can only be created by an initialize request` | You called `tools/list` (or anything else) before doing the `initialize` handshake | Follow the three-step sequence in the **MCP `tools/list`** section above — `initialize` first, capture `Mcp-Session-Id`, then send `notifications/initialized`, then call your tool |
| MCP call returns `Session not found` right after a successful `initialize` | `Invoke-WebRequest` returned the `Mcp-Session-Id` header as a string **array**, so the value sent on the next request was malformed | Use `[string]$resp.Headers['Mcp-Session-Id'][0]` (note the `[0]`) when capturing the session id |

---

## What's next

Step 5 takes this exact `dab-config.json`, drops it into a container
image, and runs it on **Azure Container Apps** — the only thing that
changes is the credential at the bottom of the chain (your `az login`
→ the step 1 UAMI). The REST/GraphQL/MCP surface stays identical.

→ [Step 5 — DAB on ACA](../05-dab-on-aca/README.md)

---

## Bring your own table

If you walked through the [step 2 BYO appendix](../02-embeddings-in-sql/byo/README.md)
and [step 3 BYO appendix](../03-hybrid-search-sp/byo/README.md), see
[byo/README.md](./byo/README.md) for how to wire your own table and SP
into DAB.
