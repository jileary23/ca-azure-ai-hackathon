"""Mock service — returns pre-processed body cam analysis results.

Used in demo/lab mode (USE_MOCK_SERVICES=true) so no Azure credentials
are required. The mock data mirrors exactly what the real Video Indexer +
GPT-4o pipeline would return.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.models.schemas import (
    AnalysisResult,
    AnalysisStatus,
    CaseSummary,
    EvidenceQueryResponse,
    EvidenceSummary,
    KeyMoment,
    Speaker,
    SpeakerRole,
    TranscriptLine,
)

_MOCK_DATA_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"

# In-memory store keyed by job_id
_STORE: dict[str, AnalysisResult] = {}


def _load_scenario(scenario_file: str = "bodycam_incident_03122024.json") -> dict:
    path = _MOCK_DATA_DIR / scenario_file
    with path.open() as f:
        return json.load(f)


def create_mock_job(case_number: str, incident_date: str | None) -> AnalysisResult:
    """Create a mock analysis job and immediately return a completed result."""
    job_id = str(uuid.uuid4())
    data = _load_scenario()

    transcript_lines = [
        TranscriptLine(
            speaker=line["speaker"],
            speaker_role=SpeakerRole(line["speaker_role"]),
            start_seconds=line["start_seconds"],
            end_seconds=line["end_seconds"],
            text=line["text"],
            confidence=line.get("confidence", 0.97),
        )
        for line in data["transcript"]
    ]

    key_moments = [
        KeyMoment(
            timestamp_seconds=m["timestamp_seconds"],
            timestamp_label=m["timestamp_label"],
            description=m["description"],
            significance=m["significance"],
            category=m["category"],
        )
        for m in data["key_moments"]
    ]

    speakers = [
        Speaker(
            id=s["id"],
            role=SpeakerRole(s["role"]),
            label=s["label"],
            total_speech_seconds=s["total_speech_seconds"],
        )
        for s in data["speakers"]
    ]

    summary_data = data["summary"]
    summary = EvidenceSummary(
        narrative=summary_data["narrative"],
        timeline=summary_data["timeline"],
        miranda_rights_read=summary_data["miranda_rights_read"],
        miranda_timestamp=summary_data.get("miranda_timestamp"),
        use_of_force_detected=summary_data["use_of_force_detected"],
        consent_given=summary_data.get("consent_given"),
        discrepancies=summary_data["discrepancies"],
        defense_considerations=summary_data["defense_considerations"],
    )

    result = AnalysisResult(
        job_id=job_id,
        case_number=case_number,
        status=AnalysisStatus.COMPLETED,
        video_duration_seconds=data["video_duration_seconds"],
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        speakers=speakers,
        transcript=transcript_lines,
        key_moments=key_moments,
        summary=summary,
        video_indexer_video_id=f"mock-vi-{job_id[:8]}",
    )

    _STORE[job_id] = result
    return result


def get_mock_job(job_id: str) -> AnalysisResult | None:
    return _STORE.get(job_id)


def list_mock_cases() -> list[CaseSummary]:
    return [
        CaseSummary(
            job_id=r.job_id,
            case_number=r.case_number,
            incident_date=None,
            status=r.status,
            video_duration_seconds=r.video_duration_seconds,
            created_at=r.created_at,
            miranda_rights_read=r.summary.miranda_rights_read if r.summary else None,
            use_of_force_detected=r.summary.use_of_force_detected
            if r.summary
            else False,
        )
        for r in _STORE.values()
    ]


def mock_query(job_id: str, question: str) -> EvidenceQueryResponse:
    """Generate a canned Q&A response based on the mock transcript."""
    result = _STORE.get(job_id)
    if not result or not result.summary:
        return EvidenceQueryResponse(
            question=question,
            answer="No analysis found for this job ID.",
            confidence="low",
        )

    q_lower = question.lower()

    # Miranda rights
    if "miranda" in q_lower or "rights" in q_lower:
        if result.summary.miranda_rights_read:
            return EvidenceQueryResponse(
                question=question,
                answer=(
                    f"Yes. Miranda rights were read at {result.summary.miranda_timestamp}. "
                    "Officer Chen stated: 'You have the right to remain silent. Anything you "
                    "say can and will be used against you in a court of law...'"
                ),
                supporting_timestamps=[result.summary.miranda_timestamp or "04:32"],
                confidence="high",
            )
        else:
            return EvidenceQueryResponse(
                question=question,
                answer=(
                    "Miranda rights do not appear to have been read prior to questioning "
                    "on the footage reviewed. The subject was asked about the vehicle before "
                    "any Miranda advisal."
                ),
                supporting_timestamps=[],
                confidence="high",
            )

    # Use of force
    if "force" in q_lower or "handcuff" in q_lower or "restrain" in q_lower:
        return EvidenceQueryResponse(
            question=question,
            answer=(
                "At 06:14, Officer Chen instructed Mr. Davis to place his hands behind his back. "
                "Mr. Davis complied. Standard handcuffing procedure was applied with no visible "
                "resistance. No additional force appears to have been used."
            ),
            supporting_timestamps=["06:14", "06:28"],
            confidence="high",
        )

    # Consent
    if "consent" in q_lower or "search" in q_lower:
        return EvidenceQueryResponse(
            question=question,
            answer=(
                "At 05:47, Officer Chen asked: 'Do you mind if I take a look in the vehicle?' "
                "Mr. Davis responded: 'I mean... I guess.' This ambiguous response was treated "
                "as consent. No explicit verbal consent was given. This may be worth challenging."
            ),
            supporting_timestamps=["05:47", "05:52"],
            confidence="high",
        )

    # Identification / stop reason
    if (
        "identify" in q_lower
        or "stop" in q_lower
        or "reason" in q_lower
        or "pull" in q_lower
    ):
        return EvidenceQueryResponse(
            question=question,
            answer=(
                "Officer Chen activated camera at 00:00 and approached the vehicle at 00:18. "
                "At 00:22, Officer Chen stated the stop was for a broken tail light. "
                "No mention of additional suspicion was made until 03:15."
            ),
            supporting_timestamps=["00:22", "03:15"],
            confidence="high",
        )

    # Fallback general answer
    return EvidenceQueryResponse(
        question=question,
        answer=(
            "Based on the body cam transcript, I reviewed the full 12-minute footage. "
            "The incident involved a traffic stop on March 12, 2024. Key events include: "
            "initial stop at 00:22, license and registration request at 01:45, "
            "vehicle search at 05:47, and arrest at 08:03. "
            "Please ask a more specific question for a detailed answer."
        ),
        supporting_timestamps=["00:22", "05:47", "08:03"],
        confidence="medium",
    )
