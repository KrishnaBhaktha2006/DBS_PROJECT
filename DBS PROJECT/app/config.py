"""
app/config.py
─────────────
Centralised settings loaded from the .env file.
All other modules import from here – never read os.environ directly.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_ENV: str = "development"

    # ── JWT ──────────────────────────────────
    JWT_SECRET_KEY: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # ── Database Driver ───────────────────────
    DB_DRIVER: str = "mysql"   # "mysql" | "oracle"

    # ── MySQL ─────────────────────────────────
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "marketplace_db"
    MYSQL_POOL_SIZE: int = 5

    # ── Oracle ────────────────────────────────
    ORACLE_USER: str = ""
    ORACLE_PASSWORD: str = ""
    ORACLE_DSN: str = ""
    ORACLE_POOL_MIN: int = 2
    ORACLE_POOL_MAX: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
