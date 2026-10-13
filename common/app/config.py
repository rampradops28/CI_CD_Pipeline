from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Common FastAPI Service"
    app_version: str = "0.1.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/test_db"

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)


settings = Settings()
