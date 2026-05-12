/*
=================================================================================
 Step 3 / SQL 03 — Smoke-test dbo.find_similar_reviews_hybrid

 Sends three demo queries to the hybrid SP and prints the ranked results.
 Each result row includes vector_rank, keyword_rank, and rrf_score so you
 can see WHY each row landed where it did.

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
DECLARE @openAiEndpoint      NVARCHAR(4000) = N'<<OPENAI_ENDPOINT>>';
DECLARE @embeddingDeployment NVARCHAR(200)  = N'<<EMBEDDING_DEPLOYMENT>>';
-- ====================================================================

IF @openAiEndpoint LIKE N'%<<OPENAI[_]ENDPOINT>>%'
   OR @embeddingDeployment LIKE N'%<<EMBEDDING[_]DEPLOYMENT>>%'
BEGIN
    RAISERROR('Set @openAiEndpoint and @embeddingDeployment above (or run via deploy.ps1).', 16, 1);
    RETURN;
END

IF RIGHT(@openAiEndpoint, 1) = N'/'
    SET @openAiEndpoint = LEFT(@openAiEndpoint, LEN(@openAiEndpoint) - 1);

PRINT '----- Query 1: semantic-leaning -----';
PRINT '"comfortable seating for long workdays"';
EXEC dbo.find_similar_reviews_hybrid
    @openAiEndpoint      = @openAiEndpoint,
    @embeddingDeployment = @embeddingDeployment,
    @queryText           = N'comfortable seating for long workdays',
    @top                 = 5;

PRINT '----- Query 2: keyword-leaning -----';
PRINT '"battery life"';
EXEC dbo.find_similar_reviews_hybrid
    @openAiEndpoint      = @openAiEndpoint,
    @embeddingDeployment = @embeddingDeployment,
    @queryText           = N'battery life',
    @top                 = 5;

PRINT '----- Query 3: mixed -----';
PRINT '"quiet keyboard for office"';
EXEC dbo.find_similar_reviews_hybrid
    @openAiEndpoint      = @openAiEndpoint,
    @embeddingDeployment = @embeddingDeployment,
    @queryText           = N'quiet keyboard for office',
    @top                 = 5;
GO
