"""Pydantic schemas for Evidence AI API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SpeakerRole(str, Enum):
    OFFICER = "officer"
    SUSPECT = "suspect"
    WITNESS = "witness"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Video submission
# ---------------------------------------------------------------------------


class VideoSubmitRequest(BaseModel):
    video_url: str | None = Field(
        default=None,
        description="Public or SAS URL to a body cam video file",
        examples=["https://storage.example.com/bodycam/incident-20240312.mp4"],
    )
    case_number: str = Field(
        description="LA County case number for tracking",
        examples=["LA-2024-CR-087421"],
    )
    incident_date: str | None = Field(
        default=None,
        description="ISO date of the incident (YYYY-MM-DD)",
        examples=["2024-03-12"],
    )
    description: str | None = Field(
        default=None,
        description="Optional context provided by the attorney",
    )
    use_mock: bool = Field(
        default=True,
        description="Use mock pre-processed data instead of calling Azure Video Indexer",
    )


class VideoSubmitResponse(BaseModel):
    job_id: str
    status: AnalysisStatus
    case_number: str
    message: str
    estimated_duration_seconds: int | None = None


# ---------------------------------------------------------------------------
# Transcript & moments
# ---------------------------------------------------------------------------


class TranscriptLine(BaseModel):
    speaker: str
    speaker_role: SpeakerRole
    start_seconds: float
    end_seconds: float
    text: str
    confidence: float = 1.0

    @property
    def timestamp(self) -> str:
        minutes, seconds = divmod(int(self.start_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"


class KeyMoment(BaseModel):
    timestamp_seconds: float
    timestamp_label: str
    description: str
    significance: str  # "high" | "medium" | "low"
    category: str  # "use_of_force" | "miranda" | "consent" | "statement" | "scene"


class Speaker(BaseModel):
    id: str
    role: SpeakerRole
    label: str
    total_speech_seconds: float


# ---------------------------------------------------------------------------
# Analysis result
# ---------------------------------------------------------------------------


class EvidenceSummary(BaseModel):
    narrative: str = Field(description="Plain-English summary of the incident")
    timeline: list[str] = Field(description="Chronological bullet-point timeline")
    miranda_rights_read: bool | None = Field(
        default=None,
        description="Whether Miranda rights were audibly read on camera",
    )
    miranda_timestamp: str | None = None
    use_of_force_detected: bool = False
    consent_given: bool | None = None
    discrepancies: list[str] = Field(
        default_factory=list,
        description="Potential inconsistencies between officer statements and visible actions",
    )
    defense_considerations: list[str] = Field(
        default_factory=list,
        description="Items flagged as potentially relevant to the defense",
    )


class AnalysisResult(BaseModel):
    job_id: str
    case_number: str
    status: AnalysisStatus
    video_duration_seconds: float | None = None
    created_at: datetime
    completed_at: datetime | None = None
    speakers: list[Speaker] = Field(default_factory=list)
    transcript: list[TranscriptLine] = Field(default_factory=list)
    key_moments: list[KeyMoment] = Field(default_factory=list)
    summary: EvidenceSummary | None = None
    video_indexer_video_id: str | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Q&A
# ---------------------------------------------------------------------------


class EvidenceQueryRequest(BaseModel):
    job_id: str = Field(description="Job ID from a completed analysis")
    question: str = Field(
        description="Natural-language question about the evidence",
        examples=[
            "Were Miranda rights read before questioning began?",
            "What happened at the 3-minute mark?",
            "Did the officer identify themselves at the start of the stop?",
        ],
    )


class EvidenceQueryResponse(BaseModel):
    question: str
    answer: str
    supporting_timestamps: list[str] = Field(default_factory=list)
    confidence: str = "high"  # "high" | "medium" | "low"


# ---------------------------------------------------------------------------
# Case list
# ---------------------------------------------------------------------------


class CaseSummary(BaseModel):
    job_id: str
    case_number: str
    incident_date: str | None
    status: AnalysisStatus
    video_duration_seconds: float | None
    created_at: datetime
    miranda_rights_read: bool | None = None
    use_of_force_detected: bool = False
