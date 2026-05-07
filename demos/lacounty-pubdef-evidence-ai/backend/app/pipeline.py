"""Orchestration pipeline — Video Indexer → GPT-4o → structured result.

Converts raw Video Indexer output into typed schemas and feeds it to
the evidence analyzer for GPT-4o summarization.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.config import get_settings
from app.models.schemas import (
    AnalysisResult,
    AnalysisStatus,
    KeyMoment,
    Speaker,
    SpeakerRole,
    TranscriptLine,
    VideoSubmitRequest,
)
from app.services.evidence_analyzer import analyze_evidence
from app.services.video_indexer_client import VideoIndexerClient

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory job store (use Azure Table Storage / Cosmos DB in production)
_JOB_STORE: dict[str, AnalysisResult] = {}


def _role_from_name(name: str) -> SpeakerRole:
    """Heuristic: Video Indexer labels speakers by number; officer is usually #1."""
    name_lower = name.lower()
    if "officer" in name_lower or "speaker 1" in name_lower:
        return SpeakerRole.OFFICER
    if "suspect" in name_lower or "speaker 2" in name_lower:
        return SpeakerRole.SUSPECT
    if "witness" in name_lower or "speaker 3" in name_lower:
        return SpeakerRole.WITNESS
    return SpeakerRole.UNKNOWN


def _parse_transcript(raw_blocks: list[dict]) -> list[TranscriptLine]:
    lines: list[TranscriptLine] = []
    for block in raw_blocks:
        speaker_name = (
            block.get("speakerDisplayName") or block.get("speakerId") or "Unknown"
        )
        for instance in block.get("instances", []):
            start = _ts_to_seconds(instance.get("start", "0:00:00.000"))
            end = _ts_to_seconds(instance.get("end", "0:00:00.000"))
            lines.append(
                TranscriptLine(
                    speaker=speaker_name,
                    speaker_role=_role_from_name(speaker_name),
                    start_seconds=start,
                    end_seconds=end,
                    text=block.get("text", ""),
                    confidence=block.get("confidence", 1.0),
                )
            )
    lines.sort(key=lambda l: l.start_seconds)
    return lines


def _ts_to_seconds(ts: str) -> float:
    """Convert 'H:MM:SS.mmm' to float seconds."""
    try:
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        if len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        return float(ts)
    except (ValueError, AttributeError):
        return 0.0


def _parse_key_moments(vi_index: dict) -> list[KeyMoment]:
    """Extract highlights and named entities that map to legal categories."""
    moments: list[KeyMoment] = []
    videos = vi_index.get("videos", [])
    if not videos:
        return moments
    insights = videos[0].get("insights", {})

    # Map Video Indexer "highlights" → KeyMoment
    for h in insights.get("highlights", []):
        for inst in h.get("instances", []):
            start = _ts_to_seconds(inst.get("start", "0"))
            minutes, seconds = divmod(int(start), 60)
            moments.append(
                KeyMoment(
                    timestamp_seconds=start,
                    timestamp_label=f"{minutes:02d}:{seconds:02d}",
                    description=h.get("text", ""),
                    significance="medium",
                    category="statement",
                )
            )

    # Map Video Indexer "labels" for scene understanding
    for label in insights.get("labels", []):
        for inst in label.get("instances", []):
            start = _ts_to_seconds(inst.get("start", "0"))
            minutes, seconds = divmod(int(start), 60)
            name = label.get("name", "")
            category = "scene"
            significance = "low"
            if any(kw in name.lower() for kw in ["handcuff", "force", "weapon", "gun"]):
                category = "use_of_force"
                significance = "high"
            moments.append(
                KeyMoment(
                    timestamp_seconds=start,
                    timestamp_label=f"{minutes:02d}:{seconds:02d}",
                    description=f"Scene: {name}",
                    significance=significance,
                    category=category,
                )
            )

    moments.sort(key=lambda m: m.timestamp_seconds)
    return moments


async def process_video(request: VideoSubmitRequest) -> AnalysisResult:
    """
    Full pipeline (production path):
    1. Submit video URL to Azure Video Indexer
    2. Poll until processing is complete
    3. Parse transcript + key moments
    4. Call GPT-4o to generate EvidenceSummary
    5. Return structured AnalysisResult
    """
    job_id = str(uuid.uuid4())

    vi_client = VideoIndexerClient(
        account_id=settings.video_indexer_account_id,
        location=settings.video_indexer_location,
        subscription_id=settings.video_indexer_subscription_id,
        resource_group=settings.video_indexer_resource_group,
        account_name=settings.video_indexer_account_name,
    )

    # --- Step 1: Submit to Video Indexer ---
    video_id = await vi_client.upload_video_url(
        video_url=request.video_url or "",
        name=f"Case-{request.case_number}",
        description=request.description or "",
    )
    logger.info("Submitted video_id=%s for job_id=%s", video_id, job_id)

    # Store pending result
    pending = AnalysisResult(
        job_id=job_id,
        case_number=request.case_number,
        status=AnalysisStatus.PROCESSING,
        created_at=datetime.now(timezone.utc),
        video_indexer_video_id=video_id,
    )
    _JOB_STORE[job_id] = pending

    # --- Step 2: Parse output (called once Video Indexer is done) ---
    vi_index = await vi_client.get_video_index(video_id)
    videos = vi_index.get("videos", [])
    duration = 0.0
    if videos:
        dur_str = (
            videos[0].get("insights", {}).get("duration", {}).get("time", "0:00:00")
        )
        duration = _ts_to_seconds(dur_str)

    raw_transcript = await vi_client.get_transcript(video_id)
    transcript = _parse_transcript(raw_transcript)
    key_moments = _parse_key_moments(vi_index)

    # Build speaker list from unique speakers in transcript
    seen: dict[str, Speaker] = {}
    for line in transcript:
        if line.speaker not in seen:
            seen[line.speaker] = Speaker(
                id=line.speaker,
                role=line.speaker_role,
                label=line.speaker,
                total_speech_seconds=0.0,
            )
        seen[line.speaker].total_speech_seconds += line.end_seconds - line.start_seconds
    speakers = list(seen.values())

    # --- Step 3: GPT-4o analysis ---
    summary = await analyze_evidence(
        transcript=transcript,
        key_moments=key_moments,
        case_context=request.description or "",
    )

    result = AnalysisResult(
        job_id=job_id,
        case_number=request.case_number,
        status=AnalysisStatus.COMPLETED,
        video_duration_seconds=duration,
        created_at=pending.created_at,
        completed_at=datetime.now(timezone.utc),
        speakers=speakers,
        transcript=transcript,
        key_moments=key_moments,
        summary=summary,
        video_indexer_video_id=video_id,
    )
    _JOB_STORE[job_id] = result
    return result


def get_job(job_id: str) -> AnalysisResult | None:
    return _JOB_STORE.get(job_id)
