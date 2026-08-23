from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Healthcare Appointment Manager"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"

    database_url: str = "postgresql+psycopg://healthcare:healthcare@localhost:5432/healthcare"
    redis_url: str = "redis://localhost:6379/0"

    hold_ttl_seconds: int = 300

    email_backend: str = "console"
    sendgrid_api_key: str = ""

    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    @field_validator("hold_ttl_seconds")
    @classmethod
    def hold_ttl_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("HOLD_TTL_SECONDS must be greater than 0")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
