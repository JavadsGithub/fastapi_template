from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Enterprise"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    # default to a local sqlite async DB to make local dev easier
    SECRET_KEY: str = "change-me-in-dev"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: List[str] = ["*"]
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
