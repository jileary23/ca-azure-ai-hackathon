"""Federated search service — mock hybrid BM25 + semantic search."""

import json
import os
from pathlib import Path

from app.models.schemas import CrossReference, DocumentResult
from app.services.mock_service import CROSS_REFERENCES_DB, DOCUMENTS_DB


_MOCK_DATA_PATH = Path(__file__).resolve().parents[2] / "mock_data" / "sample_policies.json"


def _load_sample_policies() -> list[dict]:
    """Load expanded document set from sample_policies.json, falling back to in-memory DB."""
    if _MOCK_DATA_PATH.exists():
        with open(_MOCK_DATA_PATH) as f:
            return json.load(f)
    return DOCUMENTS_DB


def _keyword_score(doc: dict, query_tokens: list[str]) -> float:
    """BM25-like keyword overlap scoring (mock)."""
    if not query_tokens:
        return doc.get("relevance_score", 0.5)

    searchable = (
        doc.get("title", "").lower()
        + " "
        + doc.get("summary", "").lower()
        + " "
        + doc.get("content_preview", "").lower()
        + " "
        + " ".join(doc.get("keywords", []))
    )
    matches = sum(1 for t in query_tokens if t.lower() in searchable)
    base = doc.get("relevance_score", 0.5)
    return min(1.0, base + matches * 0.06)


def _tokenize(query: str) -> list[str]:
    stop = {
        "the", "a", "an", "is", "are", "for", "and", "or", "to", "in",
        "of", "on", "by", "at", "from", "with", "about", "find", "show",
        "me", "search", "get", "all", "across", "state",
    }
    return [w for w in query.lower().split() if len(w) >= 2 and w not in stop]


def search(
    query: str,
    agencies: list[str] | None = None,
    doc_types: list[str] | None = None,
    limit: int = 10,
    user_permissions: list[str] | None = None,
) -> list[DocumentResult]:
    """Federated search across agency document repos."""
    from datetime import datetime

    docs = _load_sample_policies()
    tokens = _tokenize(query)
    results: list[DocumentResult] = []

    for doc in docs:
        # Agency filter
        if agencies and doc["agency"] not in agencies:
            continue
        # Doc-type filter
        if doc_types and doc["document_type"] not in doc_types:
            continue
        # Permission filter — only return docs from permitted agencies
        if user_permissions is not None and doc["agency"] not in user_permissions:
            continue

        score = _keyword_score(doc, tokens)
        results.append(
            DocumentResult(
                doc_id=doc["doc_id"],
                title=doc["title"],
                agency=doc["agency"],
                department=doc["department"],
                document_type=doc["document_type"],
                summary=doc["summary"],
                relevance_score=score,
                last_updated=datetime.fromisoformat(doc["last_updated"]),
                access_level=doc.get("access_level", "public"),
            )
        )

    results.sort(key=lambda r: r.relevance_score, reverse=True)
    return results[:limit]


def get_document_detail(doc_id: str) -> dict | None:
    """Get full document with cross-references."""
    docs = _load_sample_policies()
    target = None
    for doc in docs:
        if doc["doc_id"] == doc_id:
            target = dict(doc)
            break

    if target is None:
        # Fallback to in-memory DB
        for doc in DOCUMENTS_DB:
            if doc["doc_id"] == doc_id:
                target = dict(doc)
                break

    if target is None:
        return None

    # Attach cross-references
    refs = []
    for ref in CROSS_REFERENCES_DB:
        if ref["source_doc_id"] == doc_id or ref["target_doc_id"] == doc_id:
            refs.append(
                CrossReference(
                    source_doc_id=ref["source_doc_id"],
                    target_doc_id=ref["target_doc_id"],
                    relationship=ref["relationship"],
                    description=ref["description"],
                )
            )
    target["cross_references"] = [r.model_dump() for r in refs]
    return target
