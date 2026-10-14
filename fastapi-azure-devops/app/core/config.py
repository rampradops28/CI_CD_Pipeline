from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "FastAPI CI Project"
    app_env: str = "development"
    debug: bool = False
    port: int = 8000
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_db"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
