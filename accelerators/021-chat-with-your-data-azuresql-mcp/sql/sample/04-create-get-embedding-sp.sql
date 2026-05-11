CREATE OR ALTER PROCEDURE dbo.get_embedding
    @openAiEndpoint NVARCHAR(4000),
    @deploymentName NVARCHAR(200),
    @inputText NVARCHAR(MAX),
    @embedding VECTOR(1536) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @url NVARCHAR(4000) = CONCAT(@openAiEndpoint, '/openai/deployments/', @deploymentName, '/embeddings?api-version=2024-06-01');
    DECLARE @payload NVARCHAR(MAX) = JSON_OBJECT('input': @inputText);
    DECLARE @response NVARCHAR(MAX);

    -- Credential is resolved by URL prefix: sp_invoke_external_rest_endpoint
    -- looks up a DATABASE SCOPED CREDENTIAL whose name is the longest URL
    -- prefix matching @url. Script 03 creates one named after @openAiEndpoint.
    EXEC sp_invoke_external_rest_endpoint
        @url = @url,
        @method = 'POST',
        @payload = @payload,
        @response = @response OUTPUT;

    DECLARE @vectorJson NVARCHAR(MAX) = JSON_QUERY(@response, '$.result.data[0].embedding');
    SET @embedding = CAST(@vectorJson AS VECTOR(1536));
END
GO
