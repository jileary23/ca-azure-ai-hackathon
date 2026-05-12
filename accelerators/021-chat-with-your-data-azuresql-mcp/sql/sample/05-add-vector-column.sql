/*
Set these before running:
  :setvar OPENAI_ENDPOINT "https://<your-openai-name>.openai.azure.com"
  :setvar OPENAI_EMBEDDING_DEPLOYMENT "embedding"
*/

DECLARE @id INT;
DECLARE @text NVARCHAR(MAX);
DECLARE @embedding VECTOR(1536);

DECLARE review_cursor CURSOR FAST_FORWARD FOR
SELECT ReviewID, ReviewText
FROM dbo.ProductReviews
WHERE ReviewEmbedding IS NULL;

OPEN review_cursor;
FETCH NEXT FROM review_cursor INTO @id, @text;

WHILE @@FETCH_STATUS = 0
BEGIN
    EXEC dbo.get_embedding
        @openAiEndpoint = '$(OPENAI_ENDPOINT)',
        @deploymentName = '$(OPENAI_EMBEDDING_DEPLOYMENT)',
        @inputText = @text,
        @embedding = @embedding OUTPUT;

    UPDATE dbo.ProductReviews
    SET ReviewEmbedding = @embedding
    WHERE ReviewID = @id;

    FETCH NEXT FROM review_cursor INTO @id, @text;
END

CLOSE review_cursor;
DEALLOCATE review_cursor;
