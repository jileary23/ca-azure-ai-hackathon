"""Input validation middleware for LLM-facing accelerator agents.

Sanitizes and validates user input before it reaches the language model.
Covers: length enforcement, prompt injection detection, PII flagging,
HTML/script stripping, and Unicode normalization.

Usage:
    from shared.security import validate_input

    result = validate_input(user_text)
    if not result.is_safe:
        # reject or flag the input
        print(result.flags)
    else:
        llm_input = result.sanitized_text
"""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SecurityFlag(str, Enum):
    """Categories of security issues detected in input."""

    INPUT_TOO_LONG = "input_too_long"
    PROMPT_INJECTION = "prompt_injection"
    PII_DETECTED = "pii_detected"
    HTML_SCRIPT_DETECTED = "html_script_detected"
    SUSPICIOUS_UNICODE = "suspicious_unicode"


@dataclass
class InputValidationResult:
    """Result of input validation containing sanitized text and any flags."""

    sanitized_text: str
    original_text: str
    is_safe: bool
    flags: list[SecurityFlag] = field(default_factory=list)
    details: dict[str, list[str]] = field(default_factory=dict)

    @property
    def has_pii(self) -> bool:
        return SecurityFlag.PII_DETECTED in self.flags

    @property
    def has_injection(self) -> bool:
        return SecurityFlag.PROMPT_INJECTION in self.flags


# --- Prompt injection patterns ---
# These detect common LLM prompt injection techniques.
_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("role_override", re.compile(
        r"(?:you are now|act as|pretend (?:to be|you're)|roleplay as|"
        r"switch to|become|new persona|new role|you're now)",
        re.IGNORECASE,
    )),
    ("instruction_override", re.compile(
        r"(?:ignore (?:all |your )?(?:previous |prior |above )?instructions|"
        r"forget (?:all |your )?(?:previous |prior )?(?:instructions|rules|guidelines)|"
        r"disregard (?:all |your )?(?:previous |prior )?(?:instructions|rules)|"
        r"override (?:safety|security|your) (?:protocols?|settings?|guidelines?|rules?))",
        re.IGNORECASE,
    )),
    ("system_directive", re.compile(
        r"(?:^|\n)\s*(?:system\s*(?::|directive|update|message|prompt|override)|"
        r"admin\s*(?:override|command|directive)|"
        r"new (?:system )?directive|"
        r"authorization\s*(?:code|token|:))",
        re.IGNORECASE,
    )),
    ("output_manipulation", re.compile(
        r"(?:output (?:all|the) (?:stored|saved|cached|previous)|"
        r"(?:export|dump|list) (?:all )?(?:data|records|users|conversations)|"
        r"enter (?:maintenance|debug|transparent|developer|admin) mode|"
        r"disable (?:safety|security|content|access) (?:filters?|controls?|checks?|restrictions?))",
        re.IGNORECASE,
    )),
    ("delimiter_injection", re.compile(
        r"(?:```(?:system|admin|override)|"
        r"\[(?:INST|SYS|SYSTEM)\]|"
        r"<\|(?:im_start|system|endoftext)\|>|"
        r"<<\s*(?:SYS|SYSTEM)\s*>>)",
        re.IGNORECASE,
    )),
]

# --- PII patterns ---
# Detect common PII types to flag (not block) for review.
_PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ssn", re.compile(
        r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"
    )),
    ("email", re.compile(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
    )),
    ("phone", re.compile(
        r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    )),
    ("credit_card", re.compile(
        r"\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6(?:011|5\d{2}))[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
    )),
    ("ca_drivers_license", re.compile(
        r"\b[A-Z]\d{7}\b"
    )),
]

# --- HTML / script patterns ---
_HTML_SCRIPT_PATTERN = re.compile(
    r"<\s*/?(?:script|iframe|object|embed|form|input|link|meta|style|svg|img\s+[^>]*onerror)[^>]*>",
    re.IGNORECASE,
)
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

# --- Suspicious Unicode ---
_SUSPICIOUS_UNICODE_CATEGORIES = {"Cf", "Co", "Cn"}  # format, private use, unassigned
_HOMOGLYPH_PATTERN = re.compile(
    r"[\u200b-\u200f\u2028-\u202f\u2060-\u2064\ufeff\u00ad]"
)


class InputValidator:
    """Configurable input validation for LLM-facing agents.

    Args:
        max_length: Maximum allowed input length in characters.
        strip_html: Whether to strip HTML tags from input.
        check_pii: Whether to flag PII patterns.
        check_injection: Whether to check for prompt injection patterns.
        normalize_unicode: Whether to apply Unicode NFKC normalization.
    """

    def __init__(
        self,
        max_length: int = 2000,
        strip_html: bool = True,
        check_pii: bool = True,
        check_injection: bool = True,
        normalize_unicode: bool = True,
    ) -> None:
        self.max_length = max_length
        self.strip_html = strip_html
        self.check_pii = check_pii
        self.check_injection = check_injection
        self.normalize_unicode = normalize_unicode

    def validate(self, text: str) -> InputValidationResult:
        """Validate and sanitize input text.

        Returns an InputValidationResult with sanitized text and any security flags.
        """
        if not isinstance(text, str):
            text = str(text)

        original = text
        flags: list[SecurityFlag] = []
        details: dict[str, list[str]] = {}

        # 1. Unicode normalization (do first to catch homoglyph attacks)
        if self.normalize_unicode:
            text, unicode_flags = self._normalize_unicode(text)
            if unicode_flags:
                flags.append(SecurityFlag.SUSPICIOUS_UNICODE)
                details["suspicious_unicode"] = unicode_flags

        # 2. Length check
        if len(text) > self.max_length:
            flags.append(SecurityFlag.INPUT_TOO_LONG)
            details["length"] = [f"Input length {len(text)} exceeds maximum {self.max_length}"]
            text = text[: self.max_length]

        # 3. HTML/script stripping
        if self.strip_html:
            text, html_flags = self._strip_html(text)
            if html_flags:
                flags.append(SecurityFlag.HTML_SCRIPT_DETECTED)
                details["html_script"] = html_flags

        # 4. Prompt injection detection
        if self.check_injection:
            injection_flags = self._detect_injection(text)
            if injection_flags:
                flags.append(SecurityFlag.PROMPT_INJECTION)
                details["prompt_injection"] = injection_flags

        # 5. PII detection (flag only, don't strip)
        if self.check_pii:
            pii_flags = self._detect_pii(text)
            if pii_flags:
                flags.append(SecurityFlag.PII_DETECTED)
                details["pii"] = pii_flags

        is_safe = SecurityFlag.PROMPT_INJECTION not in flags and \
                  SecurityFlag.INPUT_TOO_LONG not in flags

        return InputValidationResult(
            sanitized_text=text.strip(),
            original_text=original,
            is_safe=is_safe,
            flags=flags,
            details=details,
        )

    def _normalize_unicode(self, text: str) -> tuple[str, list[str]]:
        """Apply NFKC normalization and detect suspicious characters."""
        flags: list[str] = []

        # Detect zero-width and homoglyph characters before normalization
        homoglyphs = _HOMOGLYPH_PATTERN.findall(text)
        if homoglyphs:
            flags.append(f"Found {len(homoglyphs)} zero-width/invisible characters")

        # Check for suspicious Unicode categories
        suspicious_chars = [
            c for c in text
            if unicodedata.category(c) in _SUSPICIOUS_UNICODE_CATEGORIES
        ]
        if suspicious_chars:
            flags.append(f"Found {len(suspicious_chars)} suspicious Unicode characters (format/private-use/unassigned)")

        # Remove zero-width characters
        text = _HOMOGLYPH_PATTERN.sub("", text)

        # NFKC normalization (collapses compatibility characters)
        text = unicodedata.normalize("NFKC", text)

        return text, flags

    def _strip_html(self, text: str) -> tuple[str, list[str]]:
        """Strip HTML tags and decode entities."""
        flags: list[str] = []

        # Check for dangerous tags first
        dangerous = _HTML_SCRIPT_PATTERN.findall(text)
        if dangerous:
            flags.append(f"Stripped {len(dangerous)} dangerous HTML elements: {dangerous[:3]}")

        # Check for any HTML tags
        all_tags = _HTML_TAG_PATTERN.findall(text)
        if all_tags:
            if not flags:
                flags.append(f"Stripped {len(all_tags)} HTML tags")
            text = _HTML_TAG_PATTERN.sub("", text)

        # Decode HTML entities
        text = html.unescape(text)

        return text, flags

    def _detect_injection(self, text: str) -> list[str]:
        """Detect known prompt injection patterns."""
        flags: list[str] = []
        for pattern_name, pattern in _INJECTION_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                flags.append(f"{pattern_name}: matched {len(matches)} pattern(s)")
        return flags

    def _detect_pii(self, text: str) -> list[str]:
        """Detect PII patterns in input (flag only, don't remove)."""
        flags: list[str] = []
        for pii_type, pattern in _PII_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                flags.append(f"{pii_type}: {len(matches)} instance(s) detected")
        return flags


# Module-level convenience instance and function
_default_validator = InputValidator()


def validate_input(
    text: str,
    *,
    max_length: Optional[int] = None,
    validator: Optional[InputValidator] = None,
) -> InputValidationResult:
    """Validate user input with sensible defaults.

    Args:
        text: The raw user input to validate.
        max_length: Override the default max length (2000 chars).
        validator: Use a custom InputValidator instance.

    Returns:
        InputValidationResult with sanitized text and security flags.
    """
    if validator is not None:
        return validator.validate(text)

    if max_length is not None:
        custom = InputValidator(max_length=max_length)
        return custom.validate(text)

    return _default_validator.validate(text)
