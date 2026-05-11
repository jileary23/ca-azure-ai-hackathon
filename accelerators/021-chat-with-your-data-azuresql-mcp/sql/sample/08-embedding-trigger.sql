CREATE OR ALTER TRIGGER dbo.trg_ProductReviews_UpdateEmbedding
ON dbo.ProductReviews
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @openAiEndpoint NVARCHAR(4000) = CONVERT(NVARCHAR(4000), SESSION_CONTEXT(N'OPENAI_ENDPOINT'));
    DECLARE @embeddingDeployment NVARCHAR(200) = CONVERT(NVARCHAR(200), SESSION_CONTEXT(N'OPENAI_EMBEDDING_DEPLOYMENT'));

    IF @openAiEndpoint IS NULL OR @embeddingDeployment IS NULL
    BEGIN
        RETURN;
    END;

    DECLARE @reviewId INT;
    DECLARE @reviewText NVARCHAR(MAX);
    DECLARE @embedding VECTOR(1536);

    DECLARE i_cursor CURSOR FAST_FORWARD FOR
    SELECT i.ReviewID, i.ReviewText
    FROM inserted i;

    OPEN i_cursor;
    FETCH NEXT FROM i_cursor INTO @reviewId, @reviewText;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        EXEC dbo.get_embedding
            @openAiEndpoint = @openAiEndpoint,
            @deploymentName = @embeddingDeployment,
            @inputText = @reviewText,
            @embedding = @embedding OUTPUT;

        UPDATE dbo.ProductReviews
        SET ReviewEmbedding = @embedding
        WHERE ReviewID = @reviewId;

        FETCH NEXT FROM i_cursor INTO @reviewId, @reviewText;
    END

    CLOSE i_cursor;
    DEALLOCATE i_cursor;
END
GO
