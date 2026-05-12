# BYO appendix — embed your own table

> Use this any time. Whether you used the sample data, skipped it, or
> both — the same recipe works for any table that has a text column you
> want to make searchable.

This appendix walks through making **your own** table embeddable using
exactly the same `dbo.get_embedding` SP and `DATABASE SCOPED CREDENTIAL`
that step 2 created. You do **not** re-create either of those.

![BYO table flow](../../../docs/architecture/05-byo-table-flow.svg)

The end-to-end picture spans steps 2 (vector column + backfill), 3
(full-text index + search SP), and 4 (DAB entities). This appendix
covers the green boxes on the **left**; the parallel BYO appendices in
[step 3](../../03-hybrid-search-sp/byo/README.md) and
[step 4](../../04-dab-local/byo/README.md) cover the rest.

---

## Assumptions

- You already finished [step 2's main lesson](../step2.md) (which created
  the credential, the SP, and the UAMI database user).
- Your table lives in the same `ProductsDB` database. (You can put it in
  a different database, but you'll need to repeat scripts 01 and 02 of
  step 2 inside that database first.)
- You can connect to the database as someone with `db_owner` or at
  least `ALTER` on the target schema, because we're going to add a
  column.

---

## 1. Add a vector column

Embeddings from `text-embedding-3-small` are **1536 floats**. The
column type is `VECTOR(1536)`.

```sql
ALTER TABLE dbo.MyDocs ADD ContentEmbedding VECTOR(1536) NULL;
```

If you ever change to a different embedding model (e.g.
`text-embedding-3-large` = 3072 dims), the column dimension must match.
You can't store a 1536-dim vector in a `VECTOR(3072)` column or vice
versa.

---

## 2. Backfill

This is identical in shape to step 2's `05-backfill-embeddings.sql` —
just point at your table + your text column.

```sql
SET NOCOUNT ON;

DECLARE @id   INT;
DECLARE @text NVARCHAR(MAX);
DECLARE @v    VECTOR(1536);

DECLARE c CURSOR FAST_FORWARD FOR
    SELECT MyDocId, Content
    FROM dbo.MyDocs
    WHERE ContentEmbedding IS NULL;

OPEN c;
FETCH NEXT FROM c INTO @id, @text;
WHILE @@FETCH_STATUS = 0
BEGIN
    EXEC dbo.get_embedding
        @openAiEndpoint = N'<paste your OPENAI_ENDPOINT here>',
        @deploymentName = N'embedding',
        @inputText      = @text,
        @embedding      = @v OUTPUT;

    UPDATE dbo.MyDocs SET ContentEmbedding = @v WHERE MyDocId = @id;

    FETCH NEXT FROM c INTO @id, @text;
END;
CLOSE c; DEALLOCATE c;
```

You can find your `OPENAI_ENDPOINT` in
`steps/01-foundation/outputs.json` under `openAiEndpoint`.

---

## 3. (Optional) Auto-embed trigger

Same structure as step 2's `06-create-auto-embed-trigger.sql`. Wrap a
trigger around your table and column. Trade-off is the same: simpler
operationally, slower INSERTs, harder to debug if the embedding endpoint
hiccups.

---

## 4. What you need before step 3 search works

Step 3 builds a hybrid (vector + keyword) search SP for `dbo.ProductReviews`.
To get the same hybrid pattern over your table, you'll need:

- The vector column (above).
- A **full-text index** on the same text column (step 3 will show you
  how on the sample table — repeat the pattern for yours).
- A copy of `dbo.find_similar_reviews_hybrid` renamed and re-pointed at
  your table.

Step 3 includes a parallel BYO appendix that walks through it.

---

## What this gives you

After this appendix, your own table has the same shape as
`dbo.ProductReviews`:

- A `VECTOR(1536)` column populated by `text-embedding-3-small`.
- The ability to compute similarity against any query string by calling
  `dbo.get_embedding` for the query then comparing with `VECTOR_DISTANCE`.

You can keep adding tables — the SP and credential are reusable.
