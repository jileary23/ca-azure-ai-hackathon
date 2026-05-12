/*
=================================================================================
 Step 2 / SQL 03 — dbo.get_embedding stored procedure

 Wraps sp_invoke_external_rest_endpoint to call:
   POST {endpoint}/openai/deployments/{deployment}/embeddings?api-version=2024-06-01
   { "input": "<text>" }

 The credential created in script 02 is matched automatically by the URL
 prefix (longest-match), so we don't pass @credential here.

 The response shape on success is:
   { "response": { "status": { "http": { "code": 200, ... } } },
     "result":   { "data": [ { "embedding": [ ... 1536 floats ... ] } ] } }

 On HTTP error the SP captured a non-200 status. We surface it with
 RAISERROR rather than silently returning NULL — that's how the previous
 version of this SP managed to put zero embeddings into the table without
 anyone noticing.
=================================================================================
*/

CREATE OR ALTER PROCEDURE dbo.get_embedding
    @openAiEndpoint  NVARCHAR(4000),
    @deploymentName  NVARCHAR(200),
    @inputText       NVARCHAR(MAX),
    @embedding       VECTOR(1536) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    SET @embedding = NULL;

    -- Normalize endpoint: strip ANY trailing slashes. The DSC created in
    -- step 2 script 02 also strips trailing slashes, so the credential's
    -- name and what we pass here must match exactly. Callers like
    -- outputs.json's openAiEndpoint sometimes carry a trailing '/'; without
    -- this trim sp_invoke_external_rest_endpoint returns:
    --   "Cannot find the credential 'https://.../', because it does not
    --    exist or you do not have permission."
    DECLARE @endpoint NVARCHAR(4000) = @openAiEndpoint;
    WHILE RIGHT(@endpoint, 1) = '/' SET @endpoint = LEFT(@endpoint, LEN(@endpoint) - 1);

    DECLARE @url NVARCHAR(4000) =
        CONCAT(@endpoint, '/openai/deployments/', @deploymentName, '/embeddings?api-version=2024-06-01');

    DECLARE @payload  NVARCHAR(MAX) = JSON_OBJECT('input': @inputText);
    DECLARE @response NVARCHAR(MAX);
    DECLARE @ret      INT;

    -- Pass @credential by NAME explicitly (URL-prefix auto-resolution
    -- silently fails in this env). The credential's NAME equals the
    -- normalized endpoint with no trailing slash.
    EXEC @ret = sp_invoke_external_rest_endpoint
        @url        = @url,
        @method     = 'POST',
        @payload    = @payload,
        @credential = @endpoint,
        @response   = @response OUTPUT;

    DECLARE @httpCode INT = TRY_CAST(JSON_VALUE(@response, '$.response.status.http.code') AS INT);

    IF @ret <> 0 OR @httpCode IS NULL OR @httpCode <> 200
    BEGIN
        DECLARE @msg NVARCHAR(2048) =
            CONCAT('Embedding call failed. return=', @ret,
                   ' httpCode=', ISNULL(CONVERT(NVARCHAR(10), @httpCode), 'NULL'),
                   ' url=', @url,
                   ' response=', LEFT(ISNULL(@response, '<null>'), 1500));
        RAISERROR(@msg, 16, 1);
        RETURN;
    END

    DECLARE @vectorJson NVARCHAR(MAX) = JSON_QUERY(@response, '$.result.data[0].embedding');

    IF @vectorJson IS NULL
    BEGIN
        DECLARE @msg2 NVARCHAR(2048) =
            CONCAT('Embedding response had no $.result.data[0].embedding. response=',
                   LEFT(ISNULL(@response, '<null>'), 1500));
        RAISERROR(@msg2, 16, 1);
        RETURN;
    END

    SET @embedding = CAST(@vectorJson AS VECTOR(1536));
END
GO

PRINT 'Created/updated stored procedure dbo.get_embedding';
GO
