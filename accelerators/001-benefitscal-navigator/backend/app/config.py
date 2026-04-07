"""Configuration for BenefitsCal Navigator."""

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
    app_name: str = "BenefitsCal Navigator"
    supported_languages: str = "en,es,zh,vi,tl,ko,hy,fa,ar"
    default_county: str = "Los Angeles"


def get_settings() -> Settings:
    return Settings()
