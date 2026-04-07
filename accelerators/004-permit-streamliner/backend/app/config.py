"""Configuration for Permit Streamliner."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    use_mock_services: bool = True
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-5.4"
    azure_search_endpoint: str = ""
    azure_search_key: str = ""
    app_name: str = "Permit Streamliner"
    max_review_days: int = 30
    supported_permit_types: str = "residential,commercial,environmental,sign,demolition"


def get_settings() -> Settings:
    return Settings()
