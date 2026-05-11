/*
=================================================================================
 Step 2 / SQL 04 — Smoke-test dbo.get_embedding on a single string

 If this succeeds you'll see one row whose json_string_length is ~30000
 (1536 floats serialized as JSON).

 If it fails, the SP now RAISERRORs with the HTTP status code and the
 raw response body so you can see what Foundry actually said. Common
 causes:
   401 -> UAMI is missing 'Cognitive Services OpenAI User' on the
          Foundry account, or the role assignment hasn't propagated.
   404 -> Deployment name doesn't match. Verify in the portal under
          your Foundry account > Deployments.
   400 -> Bad payload (input too long, etc.).

 RUNNING THIS SCRIPT
   Option A — via deploy.ps1 (recommended).
   Option B — from your SQL Editor: connect to ProductsDB, edit the two
              DECLARE lines below, and run.

   Where to find the values:
       OpenAI endpoint      -> steps/01-foundation/outputs.json field "openAiEndpoint"
       Embedding deployment -> steps/01-foundation/outputs.json field "embeddingDeployment"
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

PRINT 'Calling: ' + @openAiEndpoint + N'/openai/deployments/' + @embeddingDeployment + N'/embeddings?api-version=2024-06-01';

DECLARE @v VECTOR(1536);

EXEC dbo.get_embedding
    @openAiEndpoint  = @openAiEndpoint,
    @deploymentName  = @embeddingDeployment,
    @inputText       = N'A comfortable office chair for long work sessions.',
    @embedding       = @v OUTPUT;

SELECT
    LEN(CAST(@v AS NVARCHAR(MAX))) AS json_string_length,
    LEFT(CAST(@v AS NVARCHAR(MAX)), 80) AS embedding_preview;
GO
