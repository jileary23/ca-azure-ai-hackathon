# 03 — Hybrid search flow

What happens inside `dbo.find_similar_reviews_hybrid` when a caller
asks for the top-N reviews matching a free-text query.

![Hybrid search flow](03-hybrid-search-flow.svg)

## Reciprocal Rank Fusion

For each candidate row $r$ that appears in either the vector top-50,
the keyword top-50, or both:

$$\text{rrf}(r) = \frac{1}{k + \text{vector\_rank}(r)} + \frac{1}{k + \text{keyword\_rank}(r)}$$

with the constant $k = 60$ (the standard from
[Cormack, Clarke & Büttcher 2009](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)).
Rows that only appear in one ranker get a sentinel rank of 1000 from
the other side, so they're not eliminated outright but they're heavily
penalized — the top of the list is always dominated by rows that both
rankers agreed on.

## Why hybrid (and not just vector)

| Failure mode of pure vector search | What keyword catches |
|---|---|
| Out-of-vocabulary tokens (SKUs, error codes, model numbers) | Exact substring match |
| Typos or transliteration that the embedding model never saw | None — but vector still retrieves "close" alternatives |
| Very short queries (1–2 tokens) where embeddings are noisy | Keyword score dominates |
| Domain-specific jargon that wasn't in the embedding training data | Substring match still works |

| Failure mode of pure keyword search | What vector catches |
|---|---|
| Synonyms ("comfortable" vs "ergonomic") | Cosine similarity |
| Paraphrases ("hurts my back" vs "lower back support") | Cosine similarity |
| Conceptual queries with no overlapping keywords | Cosine similarity |

## Where this is built

| Element | Step |
|---|---|
| Full-text catalog + index               | [Step 3 — `01-create-fulltext-index.sql`](../../steps/03-hybrid-search-sp/sql/01-create-fulltext-index.sql) |
| v2 SP `(queryText, top)` (current)      | [Step 3 upgrade — `02-create-hybrid-search-sp-v2.sql`](../../steps/03-hybrid-search-sp/upgrade-external-model/sql/02-create-hybrid-search-sp-v2.sql) |
| v1 SP `(openAiEndpoint, embeddingDeployment, queryText, top)` | [Step 3 — `02-create-hybrid-search-sp.sql`](../../steps/03-hybrid-search-sp/sql/02-create-hybrid-search-sp.sql) — superseded by v2 |

## Source

Diagram is hand-authored SVG ([`03-hybrid-search-flow.svg`](03-hybrid-search-flow.svg)). Original visual source kept at [`03-hybrid-search-flow.drawio`](03-hybrid-search-flow.drawio).
