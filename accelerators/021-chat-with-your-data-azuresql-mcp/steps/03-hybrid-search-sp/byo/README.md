# BYO appendix — hybrid search over your own table

Pre-req: you already did the [step 2 BYO appendix](../../02-embeddings-in-sql/byo/README.md)
so your table has a `VECTOR(1536)` column populated with embeddings.

This appendix gives you the search SP for your table.

> **Heads up:** this guide uses the **v2 SP shape** introduced in the
> required [external-model upgrade](../upgrade-external-model/README.md).
> The SP takes `(@queryText, @top)` only — the OpenAI endpoint and
> deployment name are baked into the registered `EXTERNAL MODEL
> EmbeddingModel`. If you skipped the upgrade for some reason, copy the
> v1 SP from `sql/02-create-hybrid-search-sp.sql` instead and add the
> two extra parameters back.

---

## 1. Add a full-text index on your text column

Replace `dbo.MyDocs`, `Content`, and `PK_MyDocs` with your real names.
The `KEY INDEX` must be a single-column primary key (full-text search
doesn't support composite keys directly).

```sql
IF NOT EXISTS (SELECT 1 FROM sys.fulltext_catalogs WHERE name = 'ftCatalog')
    CREATE FULLTEXT CATALOG ftCatalog;

IF NOT EXISTS (
    SELECT 1 FROM sys.fulltext_indexes fi
    JOIN sys.tables t ON fi.object_id = t.object_id
    WHERE t.name = 'MyDocs'
)
BEGIN
    CREATE FULLTEXT INDEX ON dbo.MyDocs (Content LANGUAGE 1033)
        KEY INDEX PK_MyDocs
        ON ftCatalog;
END
```

The catalog can be shared across tables — you don't need a new one.

---

## 2. Create a search SP for your table

Copy the **v2** template from `upgrade-external-model/sql/02-create-hybrid-search-sp-v2.sql`
and rename + re-point at your table:

```sql
CREATE OR ALTER PROCEDURE dbo.find_similar_mydocs_hybrid
    @queryText NVARCHAR(MAX),
    @top       INT = 10
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @queryEmbedding VECTOR(1536);
    DECLARE @keywordQuery   NVARCHAR(4000) = LEFT(@queryText, 4000);

    SET @queryEmbedding = AI_GENERATE_EMBEDDINGS(@queryText USE MODEL EmbeddingModel);

    ;WITH vector_results AS (
        SELECT TOP (50)
            d.MyDocId,
            ROW_NUMBER() OVER (ORDER BY VECTOR_DISTANCE('cosine', d.ContentEmbedding, @queryEmbedding)) AS vector_rank,
            1.0 - VECTOR_DISTANCE('cosine', d.ContentEmbedding, @queryEmbedding) AS vector_score
        FROM dbo.MyDocs d
        WHERE d.ContentEmbedding IS NOT NULL
        ORDER BY VECTOR_DISTANCE('cosine', d.ContentEmbedding, @queryEmbedding)
    ),
    keyword_results AS (
        SELECT
            ft.[KEY] AS MyDocId,
            ROW_NUMBER() OVER (ORDER BY ft.[RANK] DESC) AS keyword_rank,
            ft.[RANK] AS keyword_score
        FROM FREETEXTTABLE(dbo.MyDocs, Content, @keywordQuery, 50) ft
    ),
    fused AS (
        SELECT
            COALESCE(v.MyDocId, k.MyDocId) AS MyDocId,
            v.vector_rank, v.vector_score,
            k.keyword_rank, k.keyword_score,
            (1.0 / (60 + COALESCE(v.vector_rank, 1000))) +
            (1.0 / (60 + COALESCE(k.keyword_rank, 1000))) AS rrf_score
        FROM vector_results v
        FULL OUTER JOIN keyword_results k ON v.MyDocId = k.MyDocId
    )
    SELECT TOP (@top)
        f.MyDocId,
        d.Content,
        f.vector_rank, f.keyword_rank,
        f.vector_score, f.keyword_score,
        f.rrf_score
    FROM fused f
    INNER JOIN dbo.MyDocs d ON d.MyDocId = f.MyDocId
    ORDER BY f.rrf_score DESC;
END
```

Make sure the UAMI has been granted `EXECUTE ON EXTERNAL MODEL :: EmbeddingModel`
— that grant happens automatically as part of the step 3 upgrade
deploy script.

---

## 3. Try it

```sql
EXEC dbo.find_similar_mydocs_hybrid
    @queryText = N'your query string',
    @top       = 5;
```

---

## What you get next

Step 4 (DAB local) and step 5 (DAB on ACA) will both expose this SP via
a REST/GraphQL endpoint. If you name your SP `find_similar_<thing>_hybrid`
the DAB config in those steps is a one-line add for each new SP.
