# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "FastAPI Enterprise"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    # default to a local sqlite async DB to make local dev easier
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    SECRET_KEY: str = "Change-me-in-dev"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: List[str] = ["*"]


settings = Settings()
