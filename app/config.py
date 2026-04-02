"""
Application settings loaded from `.env`.
"""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_ENV: str = "development"

    JWT_SECRET_KEY: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    DB_DRIVER: str = "mysql"

    MYSQL_HOST: str = Field(
        default="localhost",
        validation_alias=AliasChoices("MYSQL_HOST", "DB_HOST"),
    )
    MYSQL_PORT: int = Field(
        default=3306,
        validation_alias=AliasChoices("MYSQL_PORT", "DB_PORT"),
    )
    MYSQL_USER: str = Field(
        default="root",
        validation_alias=AliasChoices("MYSQL_USER", "DB_USER"),
    )
    MYSQL_PASSWORD: str = Field(
        default="",
        validation_alias=AliasChoices("MYSQL_PASSWORD", "DB_PASSWORD"),
    )
    MYSQL_DATABASE: str = Field(
        default="marketplace_db",
        validation_alias=AliasChoices("MYSQL_DATABASE", "DB_NAME"),
    )
    MYSQL_POOL_SIZE: int = 5

    ORACLE_USER: str = ""
    ORACLE_PASSWORD: str = ""
    ORACLE_DSN: str = ""
    ORACLE_POOL_MIN: int = 2
    ORACLE_POOL_MAX: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
