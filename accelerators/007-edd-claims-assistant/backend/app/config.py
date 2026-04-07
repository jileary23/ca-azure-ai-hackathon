"""Configuration for EDD Claims Assistant."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    use_mock_services: bool = True
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-5.2"
    azure_search_endpoint: str = ""
    azure_search_key: str = ""
    app_name: str = "EDD Claims Assistant"
    supported_claim_types: str = "UI,DI,PFL"
    identity_verification_required: bool = True


def get_settings() -> Settings:
    return Settings()
