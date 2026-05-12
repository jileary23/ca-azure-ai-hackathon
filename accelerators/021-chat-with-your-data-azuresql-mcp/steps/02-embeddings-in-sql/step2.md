# Step 2 — Embeddings in SQL

> Goal: teach Azure SQL how to call the Foundry embedding endpoint **as the
> UAMI** (no keys), wrap that in a stored procedure, and embed your seeded
> reviews so step 3's hybrid search has something to search against.
>
> Time: ~3–5 minutes (most of it waiting for `sp_invoke_external_rest_endpoint`
> to round-trip 18 rows).
>
> Cost: a fraction of a cent. `text-embedding-3-small` is ~$0.02 / 1M tokens
> and 18 short reviews is well under 1K tokens combined.

By the end of this step you will have:

- A **database user** for the UAMI created in step 1, with
  `db_datareader`, `db_datawriter`, and `EXECUTE` on `schema::dbo`.
  *(This is what lets DAB authenticate to SQL in step 5 — we set it up
  here while we're already in the database.)*
- A **`DATABASE SCOPED CREDENTIAL`** named after your OpenAI endpoint
  with `IDENTITY = 'Managed Identity'`, so SQL can acquire AAD tokens
  for HTTPS calls without a secret.
- A stored procedure **`dbo.get_embedding`** that takes text and returns
  a `VECTOR(1536)`.
- All seeded `ProductReviews` rows have a non-NULL `ReviewEmbedding`.
- *(Optional)* a trigger that auto-embeds new/updated rows.

---

## How embedding-in-SQL works

![Data and embedding flow](../../docs/architecture/02-data-and-embedding-flow.svg)

The top lane is the optional auto-embed trigger you will install at the end of this step. The bottom lane is what step 3 hybrid search SP will use. Both routes share the same DSC + UAMI auth chain. The step 3 upgrade swaps `dbo.get_embedding` for the GA primitive `AI_GENERATE_EMBEDDINGS USE MODEL EmbeddingModel`, but the credential and the identity are unchanged.

Two things make this work:

1. The **UAMI is attached** to the SQL server (done in step 1). That
   means `sp_invoke_external_rest_endpoint` has an identity to acquire
   tokens with.
2. The **UAMI has `Cognitive Services OpenAI User`** on the Foundry
   account (also done in step 1). That's the AAD role that authorizes
   the embedding endpoint call.

---

## Prerequisites

You should have already finished [step 1](../01-foundation/step1.md) and
have a `steps/01-foundation/outputs.json` file. This step's deploy
script reads that file to discover the SQL FQDN, OpenAI endpoint,
embedding deployment name, and UAMI name — you don't have to retype
anything.

You also need the same `pwsh` + `az` + `sqlcmd` toolchain from the root
README's prerequisites section.

---

## What gets created (and why each piece matters)

| Artifact | Created by | Purpose |
|---|---|---|
| `[<UAMI>]` database user | `sql/01-create-uami-db-user.sql` | Maps the UAMI to a database principal so DAB can later log in as it. Granted least-privilege roles. |
| Database master key | `sql/02-create-credential.sql` | Required by SQL before any database scoped credential can exist. Random GUID-derived password we never need again. |
| `DATABASE SCOPED CREDENTIAL` named after the endpoint | `sql/02-create-credential.sql` | Tells `sp_invoke_external_rest_endpoint` to use the SQL server's UAMI when calling that URL prefix. |
| `dbo.get_embedding` SP | `sql/03-create-get-embedding-sp.sql` | Wraps the HTTP call + JSON parsing. Returns a `VECTOR(1536)`. |
| Smoke test query | `sql/04-test-embedding.sql` | Confirms the credential, role, and SP all line up before backfilling data. |
| Backfill of `ReviewEmbedding` | `sql/05-backfill-embeddings.sql` | Embeds every NULL row. Idempotent. |
| *(Optional)* `dbo.trg_ProductReviews_AutoEmbed` | `sql/06-create-auto-embed-trigger.sql` | Auto-embeds on `INSERT`/`UPDATE`. Convenient but slows writes; install only if you want it. |

---

## Run it — pick one

You have two ways to run the SQL in this step. Pick whichever you like
better; the end state is identical.

### Option A — `deploy.ps1` (recommended)

From the repo root, in `pwsh`:

```powershell
.\steps\02-embeddings-in-sql\deploy.ps1
```

That runs scripts 01–05 in order. The slow step is **5/6** — 18
sequential HTTPS round-trips from SQL → Foundry. Expect ~10–30 seconds.

The script reads `steps/01-foundation/outputs.json`, substitutes the
`<<UAMI_NAME>>`, `<<OPENAI_ENDPOINT>>`, and `<<EMBEDDING_DEPLOYMENT>>`
placeholders in each `.sql` file, and runs the result via `sqlcmd -G`.

To also install the optional auto-embed trigger:

```powershell
.\steps\02-embeddings-in-sql\deploy.ps1 -InstallAutoEmbedTrigger
```

To create the SP and credential but **not** embed anything yet (e.g.
because you'll do BYO data only):

```powershell
.\steps\02-embeddings-in-sql\deploy.ps1 -SkipBackfill
```

### Option B — your SQL Editor (VS Code MSSQL extension, SSMS, ADS)

Each script under `sql/` has a small `DECLARE` block at the top marked
**`EDIT THIS IF RUNNING FROM YOUR SQL EDITOR`** with `<<TOKEN>>`
placeholders. Replace those with the matching values from
`steps/01-foundation/outputs.json` and run the script. If you forget,
the script raises a clear error and stops.

| Token | outputs.json field | Used by |
|---|---|---|
| `<<UAMI_NAME>>` | `uamiName` | `01-create-uami-db-user.sql` |
| `<<OPENAI_ENDPOINT>>` | `openAiEndpoint` (any trailing slash is stripped automatically) | `02`, `04`, `05`, `06` |
| `<<EMBEDDING_DEPLOYMENT>>` | `embeddingDeployment` | `04`, `05`, `06` |

> **Connect to `ProductsDB`, not `master`.** Editors default to
> `master`, where none of the tables, credential, or SP exist. In the
> VS Code MSSQL extension use the database picker; in SSMS/ADS pick
> `ProductsDB` from the database dropdown.

Run them in order: `01` → `02` → `03` → `04` → `05` → optional `06`.

---

## What the script does, mapped to files

| Section | Action | File |
|---|---|---|
| 0/6 | Reads step 1's `outputs.json` to discover the SQL FQDN, endpoint, deployment, UAMI name | `../01-foundation/outputs.json` |
| 1/6 | Creates the UAMI's database user + grants | [sql/01-create-uami-db-user.sql](sql/01-create-uami-db-user.sql) |
| 2/6 | Creates the master key + DB-scoped credential | [sql/02-create-credential.sql](sql/02-create-credential.sql) |
| 3/6 | Creates `dbo.get_embedding` | [sql/03-create-get-embedding-sp.sql](sql/03-create-get-embedding-sp.sql) |
| 4/6 | Smoke-tests the SP on one string | [sql/04-test-embedding.sql](sql/04-test-embedding.sql) |
| 5/6 | Backfills `ReviewEmbedding` for all NULL rows | [sql/05-backfill-embeddings.sql](sql/05-backfill-embeddings.sql) |
| 6/6 | *(optional)* installs the auto-embed trigger | [sql/06-create-auto-embed-trigger.sql](sql/06-create-auto-embed-trigger.sql) |

---

## Verify

### 1. The credential exists

```powershell
$fqdn = (Get-Content .\steps\01-foundation\outputs.json | ConvertFrom-Json).sqlServerFqdn
sqlcmd -S $fqdn -d ProductsDB -G -Q "SELECT name, credential_identity FROM sys.database_scoped_credentials;"
```

You should see one row whose `name` is your OpenAI endpoint and whose
`credential_identity` is `Managed Identity`.

### 2. The SP is callable and returns 1536 floats

```powershell
$out = Get-Content .\steps\01-foundation\outputs.json | ConvertFrom-Json
$endpoint = $out.openAiEndpoint.TrimEnd('/')
sqlcmd -S $out.sqlServerFqdn -d ProductsDB -G -Q @"
DECLARE @v VECTOR(1536);
EXEC dbo.get_embedding
    @openAiEndpoint  = N'$endpoint',
    @deploymentName  = N'$($out.embeddingDeployment)',
    @inputText       = N'hello world',
    @embedding       = @v OUTPUT;
SELECT LEN(CAST(@v AS NVARCHAR(MAX))) AS json_string_length;
"@
```

You should see one row with `json_string_length` ≈ 30000 (1536 floats
serialized as JSON). If you get NULL or an error, the embedding call
failed — see Troubleshooting below.

### 3. Every seeded review has an embedding

```powershell
sqlcmd -S $fqdn -d ProductsDB -G -Q "
SELECT
  COUNT(*) AS total,
  COUNT(ReviewEmbedding) AS embedded,
  COUNT(*) - COUNT(ReviewEmbedding) AS missing
FROM dbo.ProductReviews;"
```

Expect `total = 18, embedded = 18, missing = 0` if you used the default
sample data and didn't pass `-SkipBackfill`.

### 4. Spot-check one embedding

```powershell
sqlcmd -S $fqdn -d ProductsDB -G -Q "
SELECT TOP 1 ReviewID, LEFT(ReviewText, 60) AS preview,
  LEFT(CAST(ReviewEmbedding AS NVARCHAR(MAX)), 60) AS embedding_preview
FROM dbo.ProductReviews
WHERE ReviewEmbedding IS NOT NULL
ORDER BY ReviewID;"
```

You should see the preview text plus the start of the JSON-serialized
vector (`[0.0123, -0.045, ...`).

---

## Bring Your Own data

Want to embed your own table instead of, or in addition to, the sample
reviews? See [byo/README.md](byo/README.md). It walks through:

- Adding a `VECTOR(1536)` column to your table
- Reusing the same `dbo.get_embedding` SP and credential
- (Optional) auto-embed trigger for your table

You can do this any time — now, after step 3, or at the very end. The
sample-data path and the BYO path don't conflict.

---

## What it cost you

- 18 embedding requests × ~50 tokens each ≈ **900 tokens**
- 900 tokens × $0.02 / 1M tokens ≈ **$0.00002**

You will not see this on your invoice.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `failed to parse url. HRESULT: 0x80072ee6` | The literal `<<OPENAI_ENDPOINT>>` placeholder reached the SP because you ran the script without substituting the values | If using your SQL Editor, edit the `DECLARE @openAiEndpoint` line at the top. If using `deploy.ps1`, make sure `steps/01-foundation/outputs.json` exists and has `openAiEndpoint` populated. |
| `Set @openAiEndpoint above (or run via deploy.ps1).` (RAISERROR) | Same as above — placeholder wasn't replaced | Edit the DECLARE block at the top of the script, or run via `deploy.ps1` |
| `Invalid object name 'dbo.ProductReviews'` when running a script | Your editor session is connected to `master` (the default), not `ProductsDB` | In the MSSQL extension, switch the active database to `ProductsDB`; or always pass `-d ProductsDB` to `sqlcmd` |
| `Login failed for user '<token-identified principal>'` (sqlcmd) | You're signed into a different tenant than the SQL admin tenant | `az logout`, `az login --tenant <correct tenant>` |
| `The remote endpoint replied with the following status code: 401` (script 04 or 05) | UAMI doesn't have `Cognitive Services OpenAI User` on the Foundry account, **or** the role assignment hasn't propagated yet (~1 min) | Wait 60 seconds and retry; if still failing, re-check the role assignment in the portal |
| `The remote endpoint replied with the following status code: 404` | The deployment name doesn't match what was created in step 1 | Confirm `embeddingDeployment` in `outputs.json` matches a deployment under your Foundry account in the portal |
| `An invalid response was received from the upstream server` | Embedding deployment is throttling (rare at the seeded volume) or the model is being scaled | Wait, retry; this is transient |
| `Invalid object name 'dbo.ProductReviews'` | You ran step 2 before step 1, or the schema script in step 1 didn't run | Re-run step 1's deploy script (it's idempotent) |
| Backfill leaves rows NULL | One row's embedding call failed mid-loop | Re-run only `05-backfill-embeddings.sql` — it skips rows that are already embedded |
| `Cannot find the credential …` (script 04) | Script 02 didn't run, or your endpoint URL has a trailing slash mismatch | Re-run `deploy.ps1`; the script normalizes the trailing slash |

---

## Next

Open [steps/03-hybrid-search-sp/step3.md](../03-hybrid-search-sp/step3.md).
You'll add a full-text index alongside the vectors and create
`dbo.find_similar_reviews_hybrid`, which combines them with Reciprocal
Rank Fusion to get search results that are smarter than vector-only or
keyword-only on their own.
