# Step 3 (continued) — Required upgrade: `CREATE EXTERNAL MODEL` + `AI_GENERATE_EMBEDDINGS`

> Goal: replace the "pass `openAiEndpoint` and `embeddingDeployment`
> on every call" pattern with the native Azure SQL primitive that
> registers the embedding deployment as a named, reusable object.
> Net effect: `find_similar_reviews_hybrid` becomes a clean
> `(queryText, top)` call, and the MCP shape collapses to
> `execute_entity({ entity, parameters: { queryText, top } })`.
>
> Time: ~30 seconds. No new Azure resources.
>
> Prerequisites: steps 1, 2, and the main step 3 already complete
> (DSC, master key, UAMI grants, full-text index, and the original
> `find_similar_reviews_hybrid` SP all exist).

---

![Auth: v1 (per-call params) vs v2 (registered EXTERNAL MODEL)](../../../docs/architecture/04-auth-v1-v2.svg)

## Why this is split out from the main step 3 (and why it's required)

The earlier scripts intentionally used `sp_invoke_external_rest_endpoint`
+ a hand-rolled `dbo.get_embedding` SP so you could see the moving
parts: the database scoped credential, the URL composition, the bearer
token flow, the per-call parameters. That's the right teaching shape.

But shipping the SP that way leaks infrastructure config (the AOAI
endpoint URL and deployment name) into every caller — including the
MCP agent in step 6. Real users should not need to know either value.
This sub-step swaps the embedding pipeline to the GA primitives so
the SP signature drops to `(queryText, top)` and downstream steps
stop carrying that infrastructure detail.

- [`CREATE EXTERNAL MODEL`](https://learn.microsoft.com/sql/t-sql/statements/create-external-model-transact-sql)
  registers an embedding (or chat) endpoint as a named object,
  encapsulating the URL, API format, deployment name, and the
  database scoped credential to use.
- [`AI_GENERATE_EMBEDDINGS`](https://learn.microsoft.com/sql/t-sql/functions/ai-generate-embeddings-transact-sql)
  is a one-liner that calls the registered model and returns a
  `VECTOR(N)` directly:

  ```sql
  DECLARE @qv VECTOR(1536) = AI_GENERATE_EMBEDDINGS(@text USE MODEL EmbeddingModel);
  ```

---

## Availability

- ✅ **Azure SQL Database** (any current tier, including the
  `GP_S_Gen5_2` serverless DB this tutorial provisions in step 1).
- ✅ **Azure SQL Managed Instance** with the *Always-up-to-date*
  update policy.
- ✅ **SQL database in Microsoft Fabric**.
- ✅ **SQL Server 2025 (17.x)** and later.

If you're targeting an older SQL Server, stay on the original step 3
SP — the `sp_invoke_external_rest_endpoint` path works everywhere.

---

## What gets created / changed

| Artifact | Created by | Purpose |
|---|---|---|
| `EXTERNAL MODEL EmbeddingModel` | `sql/01-create-external-model.sql` | Registers the AOAI embedding deployment as a named object. Reuses the **same** DSC created in step 2. |
| `GRANT EXECUTE ON EXTERNAL MODEL :: EmbeddingModel TO <uami>` | same script | So hosted callers (DAB on ACA from step 5) can use the model. |
| `dbo.find_similar_reviews_hybrid` (replaced) | `sql/02-create-hybrid-search-sp-v2.sql` | Same body, but the signature drops `@openAiEndpoint` and `@embeddingDeployment`. Internally calls `AI_GENERATE_EMBEDDINGS` instead of `EXEC dbo.get_embedding`. |
| Smoke-test output | `sql/03-test-hybrid-search-v2.sql` | Three demo queries with the new signature. |

`dbo.get_embedding` is left in place — nothing depends on it any
more, but removing it is a cosmetic cleanup you can do later if you
want.

---

## Run it — pick one

### Option A — `deploy.ps1` (recommended)

```powershell
.\steps\03-hybrid-search-sp\upgrade-external-model\deploy.ps1
```

Substitutes `<<OPENAI_ENDPOINT>>`, `<<EMBEDDING_DEPLOYMENT>>`, and
`<<UAMI_NAME>>` from `steps/01-foundation/outputs.json` and runs all
three SQL scripts.

### Option B — your SQL Editor

Open each script under `sql/` in order, connect to **`ProductsDB`**,
and edit the `DECLARE` block at the top of script 01 with the values
below. Scripts 02 and 03 have no tokens.

| Token | outputs.json field |
|---|---|
| `<<OPENAI_ENDPOINT>>` | `openAiEndpoint` (trailing slash stripped) |
| `<<EMBEDDING_DEPLOYMENT>>` | `embeddingDeployment` |
| `<<UAMI_NAME>>` | `uamiName` |

---

## Verify

### 1. The model exists

```powershell
$fqdn = (Get-Content .\steps\01-foundation\outputs.json | ConvertFrom-Json).sqlServerFqdn
sqlcmd -S $fqdn -d ProductsDB -G -Q "SELECT name, model_type, location FROM sys.external_models;"
```

You should see `EmbeddingModel` with `model_type = EMBEDDINGS` and a
`location` ending in `/embeddings?api-version=2024-02-01`.

### 2. The SP signature changed

```powershell
sqlcmd -S $fqdn -d ProductsDB -G -Q "
SELECT p.name AS proc_name, par.name AS parameter_name, par.parameter_id
FROM sys.parameters par
JOIN sys.procedures p ON p.object_id = par.object_id
WHERE p.name = 'find_similar_reviews_hybrid'
ORDER BY par.parameter_id;"
```

You should see only `@queryText` and `@top` (the old SP had four
parameters).

### 3. End-to-end with the new shape

```powershell
sqlcmd -S $fqdn -d ProductsDB -G -Q "
EXEC dbo.find_similar_reviews_hybrid
    @queryText = N'comfortable seating for long workdays',
    @top       = 5;"
```

Same output columns (`vector_rank`, `keyword_rank`, `vector_score`,
`keyword_score`, `rrf_score`) as the original SP — RRF math is
unchanged.

---

## Downstream effects

| Layer | Change required? |
|---|---|
| Step 2 — `get_embedding` SP, DSC, master key | None. Still valid. The new model reuses the same DSC. |
| Step 3 — full-text index, RRF body | None. Index untouched, SP body identical. |
| Step 4 — local DAB | None. DAB reflects the SP signature at runtime. The entity now publishes `queryText` + `top` only. |
| Step 5 — hosted DAB on ACA | None. No image rebuild. The same container starts publishing the new signature on next request. |
| Step 6 — MCP from VS Code | The `execute_entity` call collapses to `{ entity: "FindSimilarReviewsHybrid", parameters: { queryText, top } }`. The notes about needing to feed the agent the endpoint up front go away. |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Cannot find a database scoped credential matching the location URL.` | The DSC name is not a URL prefix of the model `LOCATION`, or step 2's `02-create-credential.sql` was never run | Re-run step 2's deploy. The DSC must be named exactly `https://<account>.openai.azure.com` (no trailing slash). |
| `The user does not have permission to perform this action.` when running script 01 | UAMI is missing `REFERENCES` on the DSC | That grant is in step 2's `02-create-credential.sql` (added retroactively after the original tutorial). Re-run that step. |
| `AI_GENERATE_EMBEDDINGS returned NULL` | The REST call to AOAI failed silently — typically auth or model-name mismatch | Enable the extended event `ai_generate_embeddings_summary` to see the HTTP response code. The most common cause is the deployment name in `LOCATION` not matching an actual deployment in your Foundry/AOAI resource. |
| `external rest endpoint enabled` is off | The instance-level config wasn't set | `EXEC sp_configure 'external rest endpoint enabled', 1; RECONFIGURE WITH OVERRIDE;` (already done by step 2 in most tenants — Azure SQL Database has this enabled by default). |

---

## What's next

Re-run step 6 from VS Code and watch the call shape collapse. The
agent no longer needs to know `openAiEndpoint` or `embeddingDeployment`
at all.
