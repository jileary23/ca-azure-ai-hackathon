/*
=================================================================================
 Step 3 / Upgrade / SQL 02 — find_similar_reviews_hybrid v2 (no endpoint args)

 What changed vs. step 3 / sql / 02-create-hybrid-search-sp.sql:
   - The @openAiEndpoint and @embeddingDeployment parameters are GONE.
   - The body uses AI_GENERATE_EMBEDDINGS(... USE MODEL EmbeddingModel)
     instead of EXEC dbo.get_embedding.

 Net effect on the MCP / DAB surface:
   execute_entity({ entity: "FindSimilarReviewsHybrid", parameters: { queryText, top } })

   Callers no longer need to know the OpenAI endpoint or the deployment
   name. Both are encapsulated in the EXTERNAL MODEL created by script 01
   in this same folder.

 Idempotent: CREATE OR ALTER, safe to re-run.
=================================================================================
*/

CREATE OR ALTER PROCEDURE dbo.find_similar_reviews_hybrid
    @queryText NVARCHAR(MAX),
    @top       INT = 10
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @queryEmbedding VECTOR(1536);

    -- FREETEXTTABLE requires a non-MAX nvarchar/varchar argument; cap the input.
    DECLARE @keywordQuery NVARCHAR(4000) = LEFT(@queryText, 4000);

    -- One-liner replacement for the old EXEC dbo.get_embedding call.
    -- All endpoint/deployment/auth detail is encapsulated in EmbeddingModel.
    SET @queryEmbedding = AI_GENERATE_EMBEDDINGS(@queryText USE MODEL EmbeddingModel);

    IF @queryEmbedding IS NULL
    BEGIN
        RAISERROR('AI_GENERATE_EMBEDDINGS returned NULL for the query text. Check the EmbeddingModel definition and the ai_generate_embeddings_summary extended event.', 16, 1);
        RETURN;
    END

    ;WITH vector_results AS (
        SELECT TOP (50)
            pr.ReviewID,
            ROW_NUMBER() OVER (ORDER BY VECTOR_DISTANCE('cosine', pr.ReviewEmbedding, @queryEmbedding)) AS vector_rank,
            1.0 - VECTOR_DISTANCE('cosine', pr.ReviewEmbedding, @queryEmbedding) AS vector_score
        FROM dbo.ProductReviews pr
        WHERE pr.ReviewEmbedding IS NOT NULL
        ORDER BY VECTOR_DISTANCE('cosine', pr.ReviewEmbedding, @queryEmbedding)
    ),
    keyword_results AS (
        SELECT
            ft.[KEY] AS ReviewID,
            ROW_NUMBER() OVER (ORDER BY ft.[RANK] DESC) AS keyword_rank,
            ft.[RANK] AS keyword_score
        FROM FREETEXTTABLE(dbo.ProductReviews, ReviewText, @keywordQuery, 50) ft
    ),
    fused AS (
        SELECT
            COALESCE(v.ReviewID, k.ReviewID) AS ReviewID,
            v.vector_rank,
            v.vector_score,
            k.keyword_rank,
            k.keyword_score,
            (1.0 / (60 + COALESCE(v.vector_rank, 1000))) +
            (1.0 / (60 + COALESCE(k.keyword_rank, 1000))) AS rrf_score
        FROM vector_results v
        FULL OUTER JOIN keyword_results k ON v.ReviewID = k.ReviewID
    )
    SELECT TOP (@top)
        f.ReviewID,
        p.ProductID,
        p.Name AS ProductName,
        p.Category,
        pr.ReviewerName,
        pr.ReviewText,
        pr.Rating,
        f.vector_rank,
        f.keyword_rank,
        f.vector_score,
        f.keyword_score,
        f.rrf_score
    FROM fused f
    INNER JOIN dbo.ProductReviews pr ON pr.ReviewID = f.ReviewID
    INNER JOIN dbo.Products p        ON p.ProductID = pr.ProductID
    ORDER BY f.rrf_score DESC;
END
GO

PRINT 'Recreated dbo.find_similar_reviews_hybrid (v2 — uses EmbeddingModel, no endpoint params).';
GO
