"""Evidence analyzer — calls GPT-4o to produce structured insight from
Video Indexer transcript and key moments.

In production this runs against Azure OpenAI (your tenant, your data).
"""

from __future__ import annotations

import json
import logging

from openai import AsyncAzureOpenAI

from app.config import get_settings
from app.models.schemas import (
    EvidenceSummary,
    EvidenceQueryResponse,
    KeyMoment,
    SpeakerRole,
    TranscriptLine,
)

logger = logging.getLogger(__name__)
settings = get_settings()


def _fmt_transcript(lines: list[TranscriptLine]) -> str:
    return "\n".join(
        f"[{line.timestamp}] {line.speaker} ({line.speaker_role.value}): {line.text}"
        for line in lines
    )


def _fmt_moments(moments: list[KeyMoment]) -> str:
    return "\n".join(
        f"- [{m.timestamp_label}] {m.category.upper()}: {m.description}"
        for m in moments
    )


async def analyze_evidence(
    transcript: list[TranscriptLine],
    key_moments: list[KeyMoment],
    case_context: str = "",
) -> EvidenceSummary:
    """Send transcript + moments to GPT-4o and return a structured EvidenceSummary."""
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version="2024-05-01-preview",
    )

    system_prompt = """You are an AI legal analyst assistant for the Los Angeles County
Public Defender's Office. You analyze body cam footage transcripts to help defense
attorneys prepare their cases. Your analysis must be:
- Factual and grounded only in the transcript provided
- Focused on legally significant events (Miranda rights, consent, use of force,
  chain of custody, officer identification, stop justification)
- Neutral in tone — you flag facts; attorneys draw conclusions
- Compliant with attorney-client privilege and CJIS data handling

Respond ONLY with a valid JSON object matching the schema described."""

    user_prompt = f"""Analyze the following body cam transcript and key moments for case context:
{case_context or "Traffic stop — no additional context provided."}

=== KEY MOMENTS (from Azure Video Indexer) ===
{_fmt_moments(key_moments)}

=== FULL TRANSCRIPT ===
{_fmt_transcript(transcript)}

Return a JSON object with this exact schema:
{{
  "narrative": "<2-3 paragraph plain-English summary of the incident>",
  "timeline": ["<HH:MM — event description>", ...],
  "miranda_rights_read": true | false | null,
  "miranda_timestamp": "<MM:SS or null>",
  "use_of_force_detected": true | false,
  "consent_given": true | false | null,
  "discrepancies": ["<description of inconsistency>", ...],
  "defense_considerations": ["<legally significant item for defense>", ...]
}}"""

    response = await client.chat.completions.create(
        model=settings.azure_openai_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)

    return EvidenceSummary(
        narrative=data.get("narrative", ""),
        timeline=data.get("timeline", []),
        miranda_rights_read=data.get("miranda_rights_read"),
        miranda_timestamp=data.get("miranda_timestamp"),
        use_of_force_detected=data.get("use_of_force_detected", False),
        consent_given=data.get("consent_given"),
        discrepancies=data.get("discrepancies", []),
        defense_considerations=data.get("defense_considerations", []),
    )


async def query_evidence(
    transcript: list[TranscriptLine],
    key_moments: list[KeyMoment],
    question: str,
) -> EvidenceQueryResponse:
    """Answer an attorney's natural-language question about the evidence."""
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version="2024-05-01-preview",
    )

    system_prompt = """You are an AI legal analyst for the LA County Public Defender.
Answer questions about body cam footage based solely on the provided transcript.
Be precise, cite timestamps, and indicate confidence level."""

    user_prompt = f"""Question: {question}

=== KEY MOMENTS ===
{_fmt_moments(key_moments)}

=== TRANSCRIPT ===
{_fmt_transcript(transcript)}

Respond with JSON:
{{
  "answer": "<detailed answer citing specific timestamps and quotes>",
  "supporting_timestamps": ["MM:SS", ...],
  "confidence": "high" | "medium" | "low"
}}"""

    response = await client.chat.completions.create(
        model=settings.azure_openai_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)

    return EvidenceQueryResponse(
        question=question,
        answer=data.get("answer", ""),
        supporting_timestamps=data.get("supporting_timestamps", []),
        confidence=data.get("confidence", "medium"),
    )
