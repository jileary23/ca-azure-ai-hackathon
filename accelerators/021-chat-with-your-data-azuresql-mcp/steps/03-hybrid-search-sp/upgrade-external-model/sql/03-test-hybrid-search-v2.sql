/*
=================================================================================
 Step 3 / Upgrade / SQL 03 — Smoke test the new SP signature

 Calls dbo.find_similar_reviews_hybrid with the v2 (queryText, top) signature.
 If this works the upgrade is complete and you can re-run any client
 (DAB locally from step 4, hosted DAB from step 5, MCP from step 6) —
 they automatically pick up the simpler shape because DAB reflects the
 SP signature at runtime.
=================================================================================
*/

PRINT '--- Query 1: semantic ("comfortable seating for long workdays") ---';
EXEC dbo.find_similar_reviews_hybrid
    @queryText = N'comfortable seating for long workdays',
    @top       = 5;

PRINT '--- Query 2: keyword-heavy ("battery life") ---';
EXEC dbo.find_similar_reviews_hybrid
    @queryText = N'battery life',
    @top       = 5;

PRINT '--- Query 3: hybrid ("noise cancelling for calls") ---';
EXEC dbo.find_similar_reviews_hybrid
    @queryText = N'noise cancelling for calls',
    @top       = 5;
GO
