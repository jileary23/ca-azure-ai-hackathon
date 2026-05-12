# Step 3 — Hybrid (vector + full-text) search

> Goal: combine the embeddings from step 2 with classic full-text search
> so queries like "comfortable seating for long workdays" (semantic) and
> "battery life" (keyword) both return good results — without you having
> to pick a magic weight per query.
>
> Time: ~30 seconds. No new Azure resources.
>
> Cost: one extra embedding call per query (a fraction of a cent).

By the end of this step you will have:

- A **full-text catalog** `ftCatalog` and a **full-text index** on
  `dbo.ProductReviews(ReviewText)`.
- A stored procedure **`dbo.find_similar_reviews_hybrid`** that takes a
  free-text query and returns the top-N matches ranked by **Reciprocal
  Rank Fusion (RRF)** of vector similarity and full-text rank.
- Smoke-test output showing the SP on three demo queries with both
  component ranks visible so you can see *why* each row ranked where
  it did.

---

## Why hybrid (and why RRF)?

Two complementary failure modes:

| Approach | Strong at | Weak at |
|---|---|---|
| **Vector** (cosine over embeddings) | Paraphrase, intent ("ergonomic chair" matches "lumbar support") | Exact tokens, codes, brand names ("SKU-42", "USB-C") |
| **Full-text** (FREETEXTTABLE) | Exact and stemmed token overlap | Synonyms, paraphrases, anything the lexer doesn't know |

A naive way to combine them is a weighted sum of scores — but cosine
similarity (0–1) and the FREETEXT `RANK` (0 to ~1000) live on totally
different scales, so you'd be picking magic numbers per dataset.

**Reciprocal Rank Fusion** sidesteps that by combining **ranks** instead
of **scores**:

$$
\text{rrf}(r) = \frac{1}{k + \text{rank}_\text{vector}(r)} + \frac{1}{k + \text{rank}_\text{keyword}(r)}
$$

where $k = 60$ is the standard damping constant. A row near the top of
*both* rankings wins; a row that's #1 in one and missing from the other
still gets meaningful mass. No score normalization required.

---

## How it flows

![Hybrid search flow](../../docs/architecture/03-hybrid-search-flow.svg)

In this main step the embedding call is `dbo.get_embedding` (the step 2 wrapper around `sp_invoke_external_rest_endpoint`). The required follow-on at [upgrade-external-model](upgrade-external-model/README.md) swaps that box for `AI_GENERATE_EMBEDDINGS USE MODEL EmbeddingModel` so the SP signature collapses to `(@queryText, @top)` - the rest of the diagram is identical.

---

## Prerequisites

- [Step 1](../01-foundation/step1.md) deployed.
- [Step 2](../02-embeddings-in-sql/step2.md) complete — `dbo.get_embedding`
  exists and `ReviewEmbedding` is populated for all rows you want to
  search.

---

## What gets created

| Artifact | Created by | Purpose |
|---|---|---|
| Full-text catalog `ftCatalog` | `sql/01-create-fulltext-index.sql` | Container for full-text indexes. Shared across tables if you add more. |
| Full-text index on `dbo.ProductReviews(ReviewText)` | `sql/01-create-fulltext-index.sql` | Lets `FREETEXTTABLE` rank rows by token/stem overlap. |
| `dbo.find_similar_reviews_hybrid` SP | `sql/02-create-hybrid-search-sp.sql` | The hybrid search SP itself. Embeds the query, runs both rankings, fuses with RRF. |
| Smoke-test output | `sql/03-test-hybrid-search.sql` | Runs three demo queries and prints the ranked results. |

---

## Run it — pick one

### Option A — `deploy.ps1` (recommended)

```powershell
.\steps\03-hybrid-search-sp\deploy.ps1
```

Reads `steps/01-foundation/outputs.json`, substitutes the
`<<OPENAI_ENDPOINT>>` / `<<EMBEDDING_DEPLOYMENT>>` placeholders, and
runs scripts 01–03.

### Option B — your SQL Editor

Open each script under `sql/` in order, connect to **`ProductsDB`**
(not `master`), edit the DECLARE block at the top of `03-test-hybrid-search.sql`
with the values below, and run. Scripts 01 and 02 have no tokens to edit.

| Token | outputs.json field |
|---|---|
| `<<OPENAI_ENDPOINT>>` | `openAiEndpoint` (trailing slash stripped) |
| `<<EMBEDDING_DEPLOYMENT>>` | `embeddingDeployment` |

---

## Verify

### 1. The SP exists

```powershell
$fqdn = (Get-Content .\steps\01-foundation\outputs.json | ConvertFrom-Json).sqlServerFqdn
sqlcmd -S $fqdn -d ProductsDB -G -Q "
SELECT name FROM sys.procedures WHERE name IN ('get_embedding','find_similar_reviews_hybrid');"
```

You should see both procedures listed.

### 2. The full-text index is built

```powershell
sqlcmd -S $fqdn -d ProductsDB -G -Q "
SELECT t.name AS table_name,
       FULLTEXTCATALOGPROPERTY('ftCatalog','PopulateStatus') AS populate_status,
       OBJECTPROPERTYEX(t.object_id,'TableFullTextItemCount') AS indexed_rows
FROM sys.fulltext_indexes fi
JOIN sys.tables t ON fi.object_id = t.object_id;"
```

`populate_status = 0` means idle (done). `indexed_rows` should equal
the number of `ProductReviews` rows (18 with default sample data). If
`populate_status` is non-zero, the catalog is still building — wait a
few seconds and check again.

### 3. Try your own query

```powershell
$out = Get-Content .\steps\01-foundation\outputs.json | ConvertFrom-Json
$endpoint = $out.openAiEndpoint.TrimEnd('/')
sqlcmd -S $out.sqlServerFqdn -d ProductsDB -G -Q @"
EXEC dbo.find_similar_reviews_hybrid
    @openAiEndpoint      = N'$endpoint',
    @embeddingDeployment = N'$($out.embeddingDeployment)',
    @queryText           = N'comfortable seating for long workdays',
    @top                 = 5;
"@
```

You should get up to 5 rows back with `vector_rank`, `keyword_rank`,
`vector_score`, `keyword_score`, and `rrf_score` columns visible.

---

## Reading the output

For each query the SP returns one row per match. Key columns:

| Column | Meaning |
|---|---|
| `vector_rank` | Position in the cosine-similarity ranking (1 = closest). `NULL` if the row didn't make the top-50 by vector. |
| `keyword_rank` | Position in the FREETEXT ranking. `NULL` if the row didn't match any keywords. |
| `vector_score` | `1 − cosine_distance`. Range 0–1, higher is closer. |
| `keyword_score` | FREETEXT `RANK` value. Range 0–~1000, higher is better. |
| `rrf_score` | The fused score the SP sorted on. |

A row with `vector_rank` set but `keyword_rank = NULL` is a pure
semantic hit (the words didn't overlap). A row with both ranks set is
where hybrid earns its keep — it's strong on both signals.

---

## Bring Your Own data

Same SP shape works for any table that has:

- A `VECTOR(1536)` column (from step 2's BYO appendix), and
- A full-text index on its text column.

See [byo/README.md](byo/README.md) for the copy-and-rename recipe.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Cannot find a fulltext index for table 'dbo.ProductReviews'` | Script 01 didn't run, or it ran in `master` | Re-run via `deploy.ps1`, or in your editor confirm the active DB is `ProductsDB` |
| Zero results from all queries | Full-text catalog still populating (just created), OR no rows have `ReviewEmbedding` populated | Re-run verify query 2 above (wait until `populate_status = 0`); re-run step 2's backfill if `embedded < total` |
| `Embedding call failed. return=401 httpCode=401 …` | Same root cause as in step 2 — the SP couldn't authenticate to Foundry | This SP delegates to `dbo.get_embedding`. If step 2's smoke test currently works, this will too — re-run step 2's `deploy.ps1` first |
| Keyword rank looks weird for short queries like "a" or "the" | FREETEXT strips noise words; very short queries can return empty keyword sets | Expected behavior — the vector side still gives you results |
| Rebuilt the index, results haven't changed | Full-text indexes update asynchronously after `INSERT`/`UPDATE` | `ALTER FULLTEXT INDEX ON dbo.ProductReviews START FULL POPULATION` if you need to force a rebuild |

---

## What it cost you

- One embedding call per `EXEC dbo.find_similar_reviews_hybrid` (~$0.000001 per query at the sample volumes).
- Full-text indexing is free; it lives inside the database.

---

## Next — required: drop the per-call endpoint parameters

Before moving on to step 4, run the follow-on under
[`upgrade-external-model/`](upgrade-external-model/README.md). It
replaces the SP's `@openAiEndpoint` and `@embeddingDeployment`
parameters with a registered
[`EXTERNAL MODEL`](https://learn.microsoft.com/sql/t-sql/statements/create-external-model-transact-sql)
that the SP looks up internally via
[`AI_GENERATE_EMBEDDINGS`](https://learn.microsoft.com/sql/t-sql/functions/ai-generate-embeddings-transact-sql).

Why this is required, not optional:

- The SP you just created leaks infrastructure config (the AOAI
  endpoint URL and deployment name) into every caller — including
  the MCP agent in step 6. Real users should not need to know
  either value.
- The upgrade reuses the **same** database scoped credential and
  UAMI grants you already created in step 2; no new auth flow.
- Steps 4, 5, and 6 work without modification because DAB reflects
  the new SP signature at runtime — no image rebuild, no DAB redeploy.

After the upgrade the call shape is:

```sql
EXEC dbo.find_similar_reviews_hybrid @queryText = N'…', @top = 5;
```

and the MCP shape collapses to:

```jsonc
execute_entity({ entity: "FindSimilarReviewsHybrid", parameters: { queryText, top } })
```

→ [`upgrade-external-model/README.md`](upgrade-external-model/README.md)

Once that's done, continue to
[steps/04-dab-local/step4.md](../04-dab-local/step4.md).
