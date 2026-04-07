"""Configuration for Cross-Agency Knowledge Hub."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    use_mock_services: bool = True
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4.1"
    azure_search_endpoint: str = ""
    azure_search_key: str = ""
    app_name: str = "Cross-Agency Knowledge Hub"
    max_results_per_agency: int = 10
    enable_cross_references: bool = True


def get_settings() -> Settings:
    return Settings()
