/*
=================================================================================
 Step 3 / Upgrade / SQL 01 — Register the embedding deployment as an EXTERNAL MODEL

 What this does:
   Replaces the "pass the endpoint + deployment as parameters on every call"
   pattern with the native Azure SQL primitive: a named external model that
   wraps the same DSC + URL + API format the original dbo.get_embedding SP
   built up by hand.

   After this script runs you can call:

       DECLARE @qv VECTOR(1536) = AI_GENERATE_EMBEDDINGS(@text USE MODEL EmbeddingModel);

   from anywhere — no URL, no deployment name, no token in the call site.

 Why:
   `CREATE EXTERNAL MODEL` + `AI_GENERATE_EMBEDDINGS` are the supported
   GA primitives in Azure SQL Database (and SQL Server 2025) for exactly
   this use case. Step 2's get_embedding SP and step 3's hybrid SP were
   teaching scaffolding for the lower-level `sp_invoke_external_rest_endpoint`
   path. This script + script 02 in the same folder upgrade to the
   higher-level primitive without changing any other piece of the stack.

 Prerequisites (already true if you followed steps 1, 2, 3):
   - Database master key exists (created in step 2 / 02-create-credential.sql).
   - Database scoped credential named after the OpenAI endpoint exists, with
     IDENTITY = 'Managed Identity', SECRET = '{"resourceid":"https://cognitiveservices.azure.com"}'.
   - The UAMI has EXECUTE ANY EXTERNAL ENDPOINT and REFERENCES on the DSC
     (granted in step 2 scripts 01 and 02).

 Token (substituted by deploy.ps1, or edit by hand if running standalone):
   <<OPENAI_ENDPOINT>>     -- e.g. https://sqlrag-ai-dev-z4gsb7.openai.azure.com
   <<EMBEDDING_DEPLOYMENT>> -- e.g. embedding
   <<UAMI_NAME>>           -- e.g. sqlrag-uami-dev
=================================================================================
*/

DECLARE @openAiEndpoint nvarchar(4000) = N'<<OPENAI_ENDPOINT>>';
DECLARE @deployment     nvarchar(200)  = N'<<EMBEDDING_DEPLOYMENT>>';
DECLARE @uami           nvarchar(256)  = N'<<UAMI_NAME>>';

-- Strip trailing slash for consistent string composition.
IF RIGHT(@openAiEndpoint, 1) = N'/'
    SET @openAiEndpoint = LEFT(@openAiEndpoint, LEN(@openAiEndpoint) - 1);

-- The DSC name must be a URL prefix of the model LOCATION. Step 2's
-- 02-create-credential.sql named the DSC after the endpoint, so we can
-- reference it directly by name.
DECLARE @dscName sysname = @openAiEndpoint;

-- Build the Azure OpenAI embeddings REST URL the model will hit.
DECLARE @location nvarchar(4000) =
    @openAiEndpoint + N'/openai/deployments/' + @deployment + N'/embeddings?api-version=2024-02-01';

-- Drop and recreate so re-runs are idempotent.
IF EXISTS (SELECT 1 FROM sys.external_models WHERE name = N'EmbeddingModel')
BEGIN
    DROP EXTERNAL MODEL EmbeddingModel;
    PRINT 'Dropped existing external model EmbeddingModel.';
END

DECLARE @sql nvarchar(max) = N'
CREATE EXTERNAL MODEL EmbeddingModel
WITH (
    LOCATION   = ''' + @location + N''',
    API_FORMAT = ''Azure OpenAI'',
    MODEL_TYPE = EMBEDDINGS,
    MODEL      = ''' + @deployment + N''',
    CREDENTIAL = [' + @dscName + N']
);';

EXEC sp_executesql @sql;

PRINT 'Created EXTERNAL MODEL EmbeddingModel pointing at ' + @location;

-- Grant EXECUTE on the model itself to the UAMI used by hosted callers
-- (DAB on ACA in step 5).
DECLARE @grant nvarchar(max) =
    N'GRANT EXECUTE ON EXTERNAL MODEL :: EmbeddingModel TO ' + QUOTENAME(@uami) + N';';
EXEC sp_executesql @grant;
PRINT 'Granted EXECUTE on EXTERNAL MODEL::EmbeddingModel to ' + QUOTENAME(@uami);
GO

-- Quick smoke test to prove the model actually works end-to-end.
DECLARE @v VECTOR(1536) = AI_GENERATE_EMBEDDINGS(N'hello from CREATE EXTERNAL MODEL' USE MODEL EmbeddingModel);

IF @v IS NULL
BEGIN
    RAISERROR('AI_GENERATE_EMBEDDINGS returned NULL. Check the extended event ai_generate_embeddings_summary for the http_response_code and the underlying error from Azure OpenAI.', 16, 1);
    RETURN;
END

PRINT 'AI_GENERATE_EMBEDDINGS smoke test succeeded (returned a non-null VECTOR).';
GO
