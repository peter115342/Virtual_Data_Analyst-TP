# Configuration management using pydantic-settings

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration from environment variables
    """

    # API Settings
    fastapi_host: str = "0.0.0.0"  # nosec B104
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
    azure_ad_allowed_tenants: str | list[str] = ""
    azure_ad_allowed_audiences: str | list[str] = ""
    azure_ad_required_scope: str = "access_as_user"

    # MongoDB Settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "vda"

    # Redis Settings
    redis_url: str = "redis://localhost:6379/0"

    # Cache Settings (seconds)
    cache_schema_ttl_seconds: int = 3600
    cache_nl2sql_ttl_seconds: int = 604800
    cache_sql_results_ttl_seconds: int = 900
    cache_summary_ttl_seconds: int = 900
    cache_chat_ttl_seconds: int = 86400
    cache_max_rows: int = 2000

    # Semantic Q&A Cache (Redis) Settings
    semantic_cache_enabled: bool = True
    semantic_cache_ttl_seconds: int = 604800  # 7 days
    semantic_cache_threshold: float = 0.70
    semantic_cache_keyword_threshold: float = 0.25
    semantic_cache_keyword_weight: float = 0.25
    semantic_cache_max_candidates: int = 200
    semantic_cache_max_entries: int = 5000
    semantic_cache_embedding_model: str = "azure.text-embedding-3-small"

    # CORS Settings
    cors_origins: str | list[str] = "http://localhost:5173"

    @field_validator(
        "cors_origins",
        "azure_ad_allowed_audiences",
        "azure_ad_allowed_tenants",
        mode="before",
    )
    @classmethod
    def parse_csv_values(cls, v):
        """Parse comma-separated values from .env file"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env for backward compatibility


# Singleton instance
settings = Settings()
