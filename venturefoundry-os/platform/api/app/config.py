from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    vf_env: str = "development"
    vf_api_host: str = "0.0.0.0"
    vf_api_port: int = 8000
    vf_log_level: str = "INFO"
    vf_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8080"])

    database_url: str
    vf_db_pool_min: int = 2
    vf_db_pool_max: int = 10

    vf_jwt_algorithm: str = "HS256"
    vf_jwt_secret: str
    vf_jwt_audience: str = "venturefoundry-api"
    vf_jwt_issuer: str = "pefy-gg-identity"

    vf_dev_auth_enabled: bool = False
    vf_dev_default_user_id: str = "00000000-0000-0000-0000-000000000101"
    vf_dev_default_org_id: str = "00000000-0000-0000-0000-000000000001"
    vf_dev_default_roles: list[str] = Field(default_factory=lambda: ["viewer"])

    vf_request_timeout_seconds: int = 30

    @field_validator("vf_cors_origins", "vf_dev_default_roles", mode="before")
    @classmethod
    def split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("vf_jwt_secret")
    @classmethod
    def validate_secret(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("VF_JWT_SECRET must contain at least 32 characters")
        if value.startswith("CHANGE_ME"):
            raise ValueError("VF_JWT_SECRET must be replaced before startup")
        return value

    @field_validator("vf_db_pool_max")
    @classmethod
    def validate_pool_max(cls, value: int, info) -> int:
        minimum = info.data.get("vf_db_pool_min", 1)
        if value < minimum:
            raise ValueError("VF_DB_POOL_MAX must be greater than or equal to VF_DB_POOL_MIN")
        return value

    @property
    def is_production(self) -> bool:
        return self.vf_env.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.vf_dev_auth_enabled:
        raise RuntimeError("Development authentication cannot be enabled in production")
    return settings
