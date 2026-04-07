"""Configuration settings for Multilingual Emergency Chatbot."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    use_mock_services: bool = True
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-5.4"
    azure_translator_key: str = ""
    azure_translator_endpoint: str = ""
    azure_translator_region: str = "westus2"
    app_name: str = "Multilingual Emergency Chatbot"
    supported_languages: str = "en,es,zh,vi,tl,ko,hy,fa,ar,ja,ru,th,km,hmn,lo"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
