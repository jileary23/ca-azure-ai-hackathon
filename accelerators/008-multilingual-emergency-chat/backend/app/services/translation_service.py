"""Mock Azure Translator service for multilingual emergency chat."""

import os

SUPPORTED_LANGUAGES = [
    "en", "es", "zh-Hans", "vi", "tl", "ko", "hy", "fa",
    "ar", "ja", "ru", "th", "km", "lo", "my",
]


class TranslationService:
    """Translates text via Azure Translator (mock when USE_MOCK_SERVICES=true)."""

    def __init__(self) -> None:
        self.mock = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

    async def translate(self, text: str, target_lang: str, source_lang: str = "en") -> str:
        if self.mock:
            if target_lang == source_lang:
                return text
            return f"{text} [{target_lang}]"
        raise NotImplementedError("Real Azure Translator not configured")

    async def detect_language(self, text: str) -> str:
        if self.mock:
            return "en"
        raise NotImplementedError("Real Azure Translator not configured")

    def get_supported_languages(self) -> list[str]:
        return list(SUPPORTED_LANGUAGES)
