IF NOT EXISTS (SELECT 1 FROM sys.fulltext_catalogs WHERE name = 'ftCatalog')
BEGIN
    CREATE FULLTEXT CATALOG ftCatalog;
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.fulltext_indexes fi
    JOIN sys.tables t ON fi.object_id = t.object_id
    WHERE t.name = 'ProductReviews'
)
BEGIN
    CREATE FULLTEXT INDEX ON dbo.ProductReviews (ReviewText LANGUAGE 1033)
    KEY INDEX PK_ProductReviews
    ON ftCatalog;
END
GO
