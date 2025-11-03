# TODO: Implement configuration management using pydantic-settings


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    TODO: Add all configuration parameters from .env
    """

    # API Settings
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_env: str = "development"

    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

    # Database Settings
    database_url: str = ""
    database_readonly: bool = True

    # LLM Settings
    api_key: str = ""

    # CORS Settings
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


# Singleton instance
settings = Settings()
