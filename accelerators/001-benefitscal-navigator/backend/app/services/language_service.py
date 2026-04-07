"""Mock multi-language service for BenefitsCal Navigator."""

SUPPORTED_LANGUAGES: list[dict[str, str]] = [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "zh", "name": "Chinese (Simplified)"},
    {"code": "vi", "name": "Vietnamese"},
    {"code": "tl", "name": "Tagalog"},
    {"code": "ko", "name": "Korean"},
    {"code": "hy", "name": "Armenian"},
    {"code": "fa", "name": "Farsi"},
    {"code": "ar", "name": "Arabic"},
]

_LANG_CODES = {lang["code"] for lang in SUPPORTED_LANGUAGES}


def get_supported_languages() -> list[dict[str, str]]:
    """Return the list of supported languages with code and name."""
    return SUPPORTED_LANGUAGES


def translate(text: str, target_lang: str) -> str:
    """Mock translation — prefixes text with the target language code."""
    if target_lang == "en" or target_lang not in _LANG_CODES:
        return text
    return f"[{target_lang}] {text}"


def detect_language(text: str) -> str:
    """Mock language detection — always returns 'en'."""
    return "en"
