from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []
    DATABASE_URL: str = "sqlite+aiosqlite:///./telegram_bot.db"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8080
    LOG_LEVEL: str = "DEBUG"

    @field_validator("ADMIN_IDS", mode='before')
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v

class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    case_sensitive = True

settings = Settings()