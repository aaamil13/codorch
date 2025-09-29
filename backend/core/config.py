"""Application configuration management."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file="../config/.env.dev",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = Field(default="development")

    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/codorch_dev")
    DATABASE_POOL_SIZE: int = Field(default=5)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # AI Provider
    OPENAI_BASE_URL: str = Field(default="http://localhost:3000/v1")
    OPENAI_API_KEY: str = Field(default="")
    DEFAULT_MODEL: str = Field(default="gemini-2.5-flash")
    ADVANCED_MODEL: str = Field(default="gemini-2.5-pro")

    # AI Configuration
    AI_MAX_RETRIES: int = Field(default=3)
    AI_TIMEOUT: int = Field(default=60)
    AI_RATE_LIMIT: int = Field(default=100)

    # Authentication
    JWT_SECRET_KEY: str = Field(default="dev-secret-key")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:9000,http://localhost:3000")

    # Application
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    API_V1_PREFIX: str = Field(default="/api/v1")

    # RefMemTree
    REFMEMTREE_STORAGE_PATH: str = Field(default="./data/refmemtree")
    REFMEMTREE_CACHE_SIZE: int = Field(default=1000)

    # Vector Database
    VECTOR_DB_TYPE: str = Field(default="pgvector")
    VECTOR_DB_DIMENSIONS: int = Field(default=1536)

    # Prefect
    PREFECT_API_URL: str = Field(default="http://localhost:4200/api")

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in v.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.ENVIRONMENT == "test"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
