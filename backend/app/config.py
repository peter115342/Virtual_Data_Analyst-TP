# Configuration management using pydantic-settings

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration from environment variables
    """

    # API Settings
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_env: str = "development"

    # Database Settings
    database_url: str = ""
    database_readonly: bool = True

    # LLM Settings
    api_key: str = ""
    openai_base_url: str = "https://genai-sharedservice-emea.pwc.com/"

    # Azure Entra ID Settings
    azure_ad_client_id: str = ""
    azure_ad_tenant_id: str = ""

    # MongoDB Settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "vda"

    # CORS Settings
    cors_origins: str | list[str] = "http://localhost:5173"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins from .env file"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env for backward compatibility


# Singleton instance
settings = Settings()
