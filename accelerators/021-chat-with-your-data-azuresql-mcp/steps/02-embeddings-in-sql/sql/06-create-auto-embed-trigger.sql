/*
=================================================================================
 Step 2 / SQL 06 — (OPTIONAL) Auto-embed trigger on dbo.ProductReviews

 What it does:
   AFTER INSERT/UPDATE on dbo.ProductReviews, embed any rows whose
   ReviewText was just inserted or changed and write the result back
   into ReviewEmbedding.

 Why optional:
   * Triggers that call HTTP endpoints make INSERTs slower and harder
     to reason about (network errors propagate as INSERT errors).
   * If you only ever load reviews via a scheduled batch, just re-run
     script 05 instead of installing this trigger.

 RUNNING THIS SCRIPT
   Option A — via deploy.ps1 -InstallAutoEmbedTrigger (recommended).
   Option B — from your SQL Editor: connect to ProductsDB, edit the
              two DECLARE lines below, and run.

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

-- The trigger needs to know which Foundry endpoint + deployment to call.
-- We bake those values into the trigger body via REPLACE so any caller
-- (DAB, ad-hoc T-SQL, an app) gets auto-embedding for free without
-- having to set context first.
DECLARE @body NVARCHAR(MAX) = N'
CREATE OR ALTER TRIGGER dbo.trg_ProductReviews_AutoEmbed
ON dbo.ProductReviews
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(ReviewText) = 0
       AND NOT EXISTS (SELECT 1 FROM inserted i LEFT JOIN deleted d ON d.ReviewID = i.ReviewID WHERE d.ReviewID IS NULL)
        RETURN;

    DECLARE @id   INT;
    DECLARE @text NVARCHAR(MAX);
    DECLARE @v    VECTOR(1536);

    DECLARE c CURSOR FAST_FORWARD FOR
        SELECT i.ReviewID, i.ReviewText FROM inserted i;

    OPEN c;
    FETCH NEXT FROM c INTO @id, @text;
    WHILE @@FETCH_STATUS = 0
    BEGIN
        EXEC dbo.get_embedding
            @openAiEndpoint = N''__ENDPOINT__'',
            @deploymentName = N''__DEPLOY__'',
            @inputText      = @text,
            @embedding      = @v OUTPUT;

        UPDATE dbo.ProductReviews
        SET ReviewEmbedding = @v
        WHERE ReviewID = @id;

        FETCH NEXT FROM c INTO @id, @text;
    END;
    CLOSE c;
    DEALLOCATE c;
END;
';

SET @body = REPLACE(@body, N'__ENDPOINT__', REPLACE(@openAiEndpoint, N'''', N''''''));
SET @body = REPLACE(@body, N'__DEPLOY__',  REPLACE(@embeddingDeployment, N'''', N''''''));

EXEC sp_executesql @body;
PRINT 'Created/updated trigger dbo.trg_ProductReviews_AutoEmbed';
GO
