"""Configuration settings for GenAI Procurement Compliance Checker."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    use_mock_services: bool = True
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4.1"
    app_name: str = "GenAI Procurement Compliance Checker"
    max_upload_size_mb: int = 50
    compliance_threshold: float = 70.0

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
