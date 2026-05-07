"""Configuration for LA County Public Defender — Evidence AI Demo."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # Mock mode — set to False to use real Azure services
    use_mock_services: bool = True

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4.1"

    # Azure Video Indexer
    # See: https://learn.microsoft.com/en-us/azure/azure-video-indexer/
    video_indexer_account_id: str = ""
    video_indexer_location: str = "trial"  # e.g. "westus2" or "trial"
    video_indexer_subscription_id: str = ""
    video_indexer_resource_group: str = ""
    video_indexer_account_name: str = ""

    # App settings
    app_name: str = "LA County Public Defender — Evidence AI"
    max_video_size_mb: int = 2000


def get_settings() -> Settings:
    return Settings()
