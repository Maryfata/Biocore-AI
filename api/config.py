"""Configuration for BIOCORE AI v2.0"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./biocore_ai.db"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "dev-key-32-bytes-here-change-prod")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HIPAA_MODE: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
