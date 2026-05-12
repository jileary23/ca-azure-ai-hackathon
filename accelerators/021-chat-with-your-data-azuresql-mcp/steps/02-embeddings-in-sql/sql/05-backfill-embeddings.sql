/*
=================================================================================
 Step 2 / SQL 05 — Backfill ReviewEmbedding for every review where it's NULL

 Strategy:
   For each row in dbo.ProductReviews where ReviewEmbedding IS NULL:
     * Call dbo.get_embedding to embed ReviewText
     * UPDATE the row with the resulting VECTOR(1536)

 Notes:
   * Idempotent: rows that already have an embedding are skipped on re-runs.
     To force a full re-embed, run before this script:
        UPDATE dbo.ProductReviews SET ReviewEmbedding = NULL;
   * Token cost: text-embedding-3-small is ~$0.02 per 1M tokens. The 18
     seeded reviews cost fractions of a cent.

 RUNNING THIS SCRIPT
   Option A — via deploy.ps1 (recommended).
   Option B — from your SQL Editor: connect to ProductsDB, edit the two
              DECLARE lines below, and run.

   Where to find the values:
       OpenAI endpoint      -> steps/01-foundation/outputs.json "openAiEndpoint"
       Embedding deployment -> steps/01-foundation/outputs.json "embeddingDeployment"
=================================================================================
*/

SET NOCOUNT ON;
GO

-- ============ EDIT THESE IF RUNNING FROM YOUR SQL EDITOR ============
DECLARE @openAiEndpoint     NVARCHAR(4000) = N'<<OPENAI_ENDPOINT>>';
DECLARE @embeddingDeployment NVARCHAR(200) = N'<<EMBEDDING_DEPLOYMENT>>';
-- ====================================================================

IF @openAiEndpoint LIKE N'%<<OPENAI[_]ENDPOINT>>%'
   OR @embeddingDeployment LIKE N'%<<EMBEDDING[_]DEPLOYMENT>>%'
BEGIN
    RAISERROR('Set @openAiEndpoint and @embeddingDeployment above (or run via deploy.ps1).', 16, 1);
    RETURN;
END

IF RIGHT(@openAiEndpoint, 1) = N'/'
    SET @openAiEndpoint = LEFT(@openAiEndpoint, LEN(@openAiEndpoint) - 1);

DECLARE @id    INT;
DECLARE @text  NVARCHAR(MAX);
DECLARE @v     VECTOR(1536);
DECLARE @done  INT = 0;
DECLARE @total INT;

SELECT @total = COUNT(*) FROM dbo.ProductReviews WHERE ReviewEmbedding IS NULL;
PRINT CONCAT('Rows to embed: ', @total);

DECLARE c CURSOR FAST_FORWARD FOR
    SELECT ReviewID, ReviewText
    FROM dbo.ProductReviews
    WHERE ReviewEmbedding IS NULL
    ORDER BY ReviewID;

OPEN c;
FETCH NEXT FROM c INTO @id, @text;

WHILE @@FETCH_STATUS = 0
BEGIN
    EXEC dbo.get_embedding
        @openAiEndpoint = @openAiEndpoint,
        @deploymentName = @embeddingDeployment,
        @inputText      = @text,
        @embedding      = @v OUTPUT;

    UPDATE dbo.ProductReviews
    SET ReviewEmbedding = @v
    WHERE ReviewID = @id;

    SET @done += 1;
    PRINT CONCAT('  embedded ReviewID=', @id, '  (', @done, '/', @total, ')');

    FETCH NEXT FROM c INTO @id, @text;
END;

CLOSE c;
DEALLOCATE c;

DECLARE @remaining INT;
SELECT @remaining = COUNT(*) FROM dbo.ProductReviews WHERE ReviewEmbedding IS NULL;
PRINT CONCAT('Done. Rows still NULL: ', @remaining);
GO
