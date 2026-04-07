"""Tests for the document analysis and completeness services."""

import pytest
from app.services.document_service import (
    analyze_document,
    check_document_completeness,
    MOCK_EXTRACTIONS,
    REQUIRED_DOCUMENTS,
    SUPPORTED_DOCUMENT_TYPES,
)


# ── analyze_document ──────────────────────────────────────────────────

class TestAnalyzeDocument:
    def test_w2_extraction(self):
        result = analyze_document("w2")
        assert result["document_type"] == "w2"
        assert result["confidence"] == 0.95
        assert "wages" in result["extracted_data"]
        assert result["fields_found"] == len(MOCK_EXTRACTIONS["w2"])

    def test_pay_stub_extraction(self):
        result = analyze_document("pay_stub")
        assert result["document_type"] == "pay_stub"
        assert "gross_pay" in result["extracted_data"]

    def test_tax_return_extraction(self):
        result = analyze_document("tax_return")
        assert result["document_type"] == "tax_return"
        assert "agi" in result["extracted_data"]

    def test_bank_statement_extraction(self):
        result = analyze_document("bank_statement")
        assert result["document_type"] == "bank_statement"
        assert "ending_balance" in result["extracted_data"]

    def test_unsupported_type(self):
        result = analyze_document("passport")
        assert result["confidence"] == 0.0
        assert result["fields_found"] == 0
        assert "error" in result

    def test_case_insensitive(self):
        result = analyze_document("W2")
        assert result["document_type"] == "w2"
        assert result["confidence"] > 0

    def test_content_param_accepted(self):
        result = analyze_document("w2", content="some raw content")
        assert result["confidence"] == 0.95


# ── check_document_completeness ──────────────────────────────────────

class TestCheckDocumentCompleteness:
    def test_all_standard_submitted(self):
        result = check_document_completeness(
            submitted_docs=REQUIRED_DOCUMENTS["standard"],
            application_type="standard",
        )
        assert result["complete"] is True
        assert len(result["missing"]) == 0
        assert result["progress_pct"] == 100.0

    def test_partial_submission(self):
        result = check_document_completeness(
            submitted_docs=["photo_id"],
            application_type="standard",
        )
        assert result["complete"] is False
        assert len(result["missing"]) > 0
        assert 0 < result["progress_pct"] < 100

    def test_empty_submission(self):
        result = check_document_completeness(
            submitted_docs=[],
            application_type="standard",
        )
        assert result["complete"] is False
        assert result["progress_pct"] == 0.0

    def test_pregnancy_application_type(self):
        result = check_document_completeness(
            submitted_docs=REQUIRED_DOCUMENTS["standard"],
            application_type="pregnancy",
        )
        assert result["complete"] is False
        assert "proof_of_pregnancy" in result["missing"]

    def test_disability_requires_extra_docs(self):
        result = check_document_completeness(
            submitted_docs=REQUIRED_DOCUMENTS["standard"],
            application_type="disability",
        )
        assert result["complete"] is False
        assert "disability_certification" in result["missing"]

    def test_extra_documents_ignored_gracefully(self):
        result = check_document_completeness(
            submitted_docs=REQUIRED_DOCUMENTS["standard"] + ["random_extra_doc"],
            application_type="standard",
        )
        assert result["complete"] is True
