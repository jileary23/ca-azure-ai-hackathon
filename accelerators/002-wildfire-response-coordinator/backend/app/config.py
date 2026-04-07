"""Configuration settings for Wildfire Response Coordinator."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Wildfire Response Coordinator"
    use_mock_services: bool = True

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-5.2"
    azure_openai_api_version: str = "2024-02-15-preview"

    # Azure Maps
    azure_maps_key: str = ""

    # Wildfire-specific
    mutual_aid_regions: str = "1,2,3,4,5,6"
    psps_coordination_enabled: bool = True

    model_config = {"env_prefix": "", "case_sensitive": False}


def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings(
        use_mock_services=os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    )
