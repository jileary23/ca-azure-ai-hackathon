"""Configuration settings for Medi-Cal Eligibility Agent."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Medi-Cal Eligibility Agent"
    use_mock_services: bool = True

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-5.2"
    azure_openai_api_version: str = "2024-02-15-preview"

    # Azure Document Intelligence
    azure_document_intelligence_endpoint: str = ""
    azure_document_intelligence_key: str = ""

    # FPL 2024 Guidelines
    fpl_2024_individual: int = 15060
    fpl_2024_per_additional: int = 5380

    model_config = {"env_prefix": "", "case_sensitive": False}


def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings(
        use_mock_services=os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    )
