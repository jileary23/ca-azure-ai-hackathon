# 02 — Data and embedding flow

How a row of free text becomes a searchable vector. The whole pipeline
runs **inside Azure SQL** — the application tier never sees an
embeddings request or an API key.

![Data and embedding flow](02-data-and-embedding-flow.svg)

## Insert path (auto-embed trigger)

When the optional `AFTER INSERT` trigger is installed, every new row
flows top-lane in the diagram above:

1. Caller does an `INSERT INTO dbo.ProductReviews(...)`.
2. Trigger fires; calls `AI_GENERATE_EMBEDDINGS(@ReviewText USE MODEL EmbeddingModel)`.
3. The EXTERNAL MODEL uses the DSC to acquire an MI bearer token, then POSTs to the `embedding` deployment.
4. Azure OpenAI returns a 1536-dim vector; the trigger writes it back to the row's `ReviewEmbedding` column.

Without the trigger you call [`05-backfill-embeddings.sql`](../../steps/02-embeddings-in-sql/sql/05-backfill-embeddings.sql)
in batch — same model, same auth, just driven from a cursor instead of
a trigger.

## Query-time path (search SP)

The bottom lane in the diagram. The SP takes only `(@queryText, @top)`,
uses `AI_GENERATE_EMBEDDINGS` to vectorize the query against the same
registered model, runs vector + keyword rankers, and fuses the two
rankings with RRF before returning the top-N rows.

## Why this design

- **No secrets cross the wire.** The DSC is `IDENTITY = 'Managed
  Identity'`. SQL acquires its own bearer token via the UAMI and never
  stores an API key.
- **One round-trip per call.** `AI_GENERATE_EMBEDDINGS` is a built-in
  function once the `EXTERNAL MODEL` is registered. Callers don't have
  to know the OpenAI endpoint or deployment name — those are baked into
  the model registration.
- **The trigger is optional.** You can use the manual backfill
  ([`05-backfill-embeddings.sql`](../../steps/02-embeddings-in-sql/sql/05-backfill-embeddings.sql))
  in batch jobs and skip the trigger, or install the trigger and have
  every new row auto-embed. Both paths use the exact same model.
- **Idempotency.** `AI_GENERATE_EMBEDDINGS` is deterministic for the
  same input + model deployment, so re-running the backfill on already-
  embedded rows is a no-op.

## Where each piece is built

| Element                                   | Step |
|-------------------------------------------|------|
| `DATABASE SCOPED CREDENTIAL` (MI)         | [Step 2 — `02-create-credential.sql`](../../steps/02-embeddings-in-sql/sql/02-create-credential.sql) |
| Auto-embed trigger                        | [Step 2 — `06-create-auto-embed-trigger.sql`](../../steps/02-embeddings-in-sql/sql/06-create-auto-embed-trigger.sql) |
| Backfill cursor                           | [Step 2 — `05-backfill-embeddings.sql`](../../steps/02-embeddings-in-sql/sql/05-backfill-embeddings.sql) |
| `EXTERNAL MODEL EmbeddingModel`           | [Step 3 upgrade — `01-create-external-model.sql`](../../steps/03-hybrid-search-sp/upgrade-external-model/sql/01-create-external-model.sql) |
| v2 search SP that uses the model          | [Step 3 upgrade — `02-create-hybrid-search-sp-v2.sql`](../../steps/03-hybrid-search-sp/upgrade-external-model/sql/02-create-hybrid-search-sp-v2.sql) |

## Source

Diagram is hand-authored SVG ([`02-data-and-embedding-flow.svg`](02-data-and-embedding-flow.svg)). Original visual source kept at [`02-data-and-embedding-flow.drawio`](02-data-and-embedding-flow.drawio).
